import hashlib
import hmac
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app
from app.store import Store


class FacebookWebhookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_facebook_webhook_verification_challenge(self):
        app = create_app(self.tmp_path, start_worker=False)
        with TestClient(app) as client:
            # Without token configured -> 503
            resp = client.get('/api/webhooks/facebook?hub_mode=subscribe&hub_verify_token=mytoken&hub_challenge=12345')
            self.assertEqual(resp.status_code, 503)

            # Configure facebook_verify_token
            settings = client.get('/api/settings').json()
            payload = {k: settings[k] for k in ('provider', 'model', 'brand', 'channel_settings', 'data_mode')}
            payload['social_keys'] = {'facebook_verify_token': 'test_verify_token_123'}
            self.assertEqual(client.put('/api/settings', json=payload).status_code, 200)

            # Wrong token -> 403
            resp = client.get('/api/webhooks/facebook?hub_mode=subscribe&hub_verify_token=wrong&hub_challenge=12345')
            self.assertEqual(resp.status_code, 403)

            # Correct token -> 200 plain text challenge
            resp = client.get('/api/webhooks/facebook?hub_mode=subscribe&hub_verify_token=test_verify_token_123&hub_challenge=challenge_accepted')
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.text, 'challenge_accepted')

    def test_facebook_webhook_comment_received_and_replied(self):
        app = create_app(self.tmp_path, start_worker=False)
        with TestClient(app) as client:
            # 1. Configure settings with facebook tokens
            settings = client.get('/api/settings').json()
            payload = {k: settings[k] for k in ('provider', 'model', 'brand', 'channel_settings', 'data_mode')}
            app_secret = 'super_secret_fb_app_key'
            payload['social_keys'] = {
                'facebook_verify_token': 'mytoken',
                'facebook_app_secret': app_secret,
                'facebook_page_token': 'EAAB123pageToken',
                'facebook_page_id': '10987654321',
            }
            self.assertEqual(client.put('/api/settings', json=payload).status_code, 200)

            # 2. Create a campaign and simulate confirmed Facebook publication receipt
            campaign = client.post('/api/campaigns', json={
                'title': 'FB Campaign',
                'audience': 'Business owners',
                'goal': 'Leads',
            }).json()
            campaign_id = campaign['id']

            store = app.state.store
            c = store.get(campaign_id)
            c['results']['publishing'] = {
                'state': 'COMPLETED',
                'output': {
                    'mode': 'live',
                    'receipts': [{
                        'platform': 'facebook',
                        'post_id': '10987654321_99887766',
                        'timestamp': 1700000000,
                    }]
                }
            }
            with store.transaction() as db:
                Store.write(db, c)

            # 3. Simulate incoming Facebook webhook POST payload
            fb_payload = {
                "object": "page",
                "entry": [
                    {
                        "id": "10987654321",
                        "time": 1700000010,
                        "changes": [
                            {
                                "field": "feed",
                                "value": {
                                    "item": "comment",
                                    "verb": "add",
                                    "comment_id": "comment_abc_123",
                                    "post_id": "10987654321_99887766",
                                    "from": {"name": "Jane Customer", "id": "user_456"},
                                    "message": "How much does this package cost and what is included?"
                                }
                            }
                        ]
                    }
                ]
            }
            raw_body = json.dumps(fb_payload).encode('utf-8')
            sig = 'sha256=' + hmac.new(app_secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()

            # Wrong signature -> 401
            res = client.post('/api/webhooks/facebook', content=raw_body, headers={'x-hub-signature-256': 'sha256=invalid'})
            self.assertEqual(res.status_code, 401)

            # Valid signature -> 200 and comment queued
            res = client.post('/api/webhooks/facebook', content=raw_body, headers={'x-hub-signature-256': sig})
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()['matched_comments'], 1)

            # Check engagement inbox
            inbox = client.get('/api/engagement').json()
            self.assertEqual(len(inbox), 1)
            item = inbox[0]
            self.assertEqual(item['platform'], 'facebook')
            self.assertEqual(item['author'], 'Jane Customer')
            self.assertEqual(item['text'], 'How much does this package cost and what is included?')
            self.assertEqual(item['state'], 'QUEUED')

            # 4. Step community worker to generate draft reply
            community = app.state.community
            stepped = community.step()
            self.assertTrue(stepped)

            inbox_after = client.get('/api/engagement').json()
            item_after = inbox_after[0]
            self.assertEqual(item_after['state'], 'AWAITING_APPROVAL')
            self.assertIn('output', item_after)
            draft_hash = item_after['draft_hash']

            # 5. Approve reply -> mocks Graph API call
            mock_fb_resp = MagicMock()
            mock_fb_resp.status_code = 200
            mock_fb_resp.json.return_value = {'id': 'reply_comment_999'}

            with patch('httpx.post', return_value=mock_fb_resp) as mock_post:
                decide_res = client.post(f'/api/engagement/{item_after["id"]}/decision', json={
                    'draft_hash': draft_hash,
                    'approve': True,
                })
                self.assertEqual(decide_res.status_code, 200)
                decided = decide_res.json()
                self.assertEqual(decided['state'], 'APPROVED')
                self.assertEqual(decided.get('facebook_reply_id'), 'reply_comment_999')
                self.assertTrue(decided.get('facebook_reply_posted'))
                self.assertTrue(mock_post.called)
                call_url = mock_post.call_args[0][0]
                self.assertIn('comment_abc_123/comments', call_url)


if __name__ == '__main__':
    unittest.main()
