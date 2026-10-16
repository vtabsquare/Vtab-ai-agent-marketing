import base64
import hashlib
import hmac
import json
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

from fastapi.testclient import TestClient

from app.integrations import Channel
from app.main import create_app
from app.store import Store
from app.tools import CheckFailure


class InstagramIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_instagram_channel_publish_success(self):
        keys = {
            'instagram_account_id': '178414123456789',
            'facebook_page_token': 'test_meta_page_token',
            'facebook_page_id': '10001234567',
        }
        channel = Channel('instagram', keys)
        sample_b64 = 'data:image/png;base64,' + base64.b64encode(b'fake_png_data').decode()

        # Mock Facebook photo upload response
        mock_fb_photo = MagicMock()
        mock_fb_photo.status_code = 200
        mock_fb_photo.json.return_value = {'id': 'photo_111'}

        # Mock CDN response
        mock_cdn_resp = MagicMock()
        mock_cdn_resp.status_code = 200
        mock_cdn_resp.json.return_value = {'images': [{'source': 'https://scontent.fbcdn.net/creative.png'}]}

        # Mock Instagram container creation
        mock_container_resp = MagicMock()
        mock_container_resp.status_code = 200
        mock_container_resp.json.return_value = {'id': 'creation_container_999'}

        # Mock Instagram status check
        mock_status_resp = MagicMock()
        mock_status_resp.status_code = 200
        mock_status_resp.json.return_value = {'status_code': 'FINISHED'}

        # Mock Instagram media publish
        mock_publish_resp = MagicMock()
        mock_publish_resp.status_code = 200
        mock_publish_resp.json.return_value = {'id': '17999888777666'}

        # Mock Instagram media info
        mock_info_resp = MagicMock()
        mock_info_resp.status_code = 200
        mock_info_resp.json.return_value = {'permalink': 'https://www.instagram.com/p/DB12345/'}

        def mock_post_side_effect(url, *args, **kwargs):
            if 'photos' in url:
                return mock_fb_photo
            if 'media_publish' in url:
                return mock_publish_resp
            if 'media' in url:
                return mock_container_resp
            return MagicMock(status_code=200, json=lambda: {})

        def mock_get_side_effect(url, *args, **kwargs):
            if 'photo_111' in url:
                return mock_cdn_resp
            if 'creation_container_999' in url:
                return mock_status_resp
            if '17999888777666' in url:
                return mock_info_resp
            return MagicMock(status_code=200, json=lambda: {})

        with patch('httpx.post', side_effect=mock_post_side_effect), \
             patch('httpx.get', side_effect=mock_get_side_effect):
            receipt = channel.publish('Exciting new product launch! #tech #startup', image_b64=sample_b64)
            self.assertEqual(receipt['platform'], 'instagram')
            self.assertEqual(receipt['post_id'], '17999888777666')
            self.assertEqual(receipt['status'], 'published')
            self.assertEqual(receipt['url'], 'https://www.instagram.com/p/DB12345/')

    def test_instagram_channel_publish_requires_image(self):
        keys = {
            'instagram_account_id': '178414123456789',
            'instagram_access_token': 'token123',
        }
        channel = Channel('instagram', keys)
        with self.assertRaises(CheckFailure) as ctx:
            channel.publish('Text only post', image_b64=None)
        self.assertIn('require an image attachment', str(ctx.exception))

    def test_instagram_webhook_challenge_verification(self):
        app = create_app(self.tmp_path, start_worker=False)
        with TestClient(app) as client:
            # Configure verify token
            settings = client.get('/api/settings').json()
            payload = {k: settings[k] for k in ('provider', 'model', 'brand', 'channel_settings', 'data_mode')}
            payload['social_keys'] = {'instagram_verify_token': 'ig_verify_token_456'}
            self.assertEqual(client.put('/api/settings', json=payload).status_code, 200)

            # Test verification
            res = client.get('/api/webhooks/instagram?hub_mode=subscribe&hub_verify_token=ig_verify_token_456&hub_challenge=ig_challenge_accepted')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.text, 'ig_challenge_accepted')

    def test_instagram_webhook_comment_and_reply_approval(self):
        app = create_app(self.tmp_path, start_worker=False)
        with TestClient(app) as client:
            # 1. Configure settings
            settings = client.get('/api/settings').json()
            payload = {k: settings[k] for k in ('provider', 'model', 'brand', 'channel_settings', 'data_mode')}
            app_secret = 'ig_meta_app_secret'
            payload['social_keys'] = {
                'facebook_app_secret': app_secret,
                'instagram_verify_token': 'ig_token',
                'instagram_account_id': '178414123456789',
                'facebook_page_token': 'EAA_valid_token',
            }
            self.assertEqual(client.put('/api/settings', json=payload).status_code, 200)

            # 2. Create campaign with an Instagram published post receipt
            campaign = client.post('/api/campaigns', json={
                'title': 'Instagram Campaign',
                'audience': 'Developers',
                'goal': 'Community growth',
            }).json()
            campaign_id = campaign['id']

            store = app.state.store
            c = store.get(campaign_id)
            c['results']['publishing'] = {
                'state': 'COMPLETED',
                'output': {
                    'mode': 'live',
                    'receipts': [{
                        'platform': 'instagram',
                        'post_id': '17999888777666',
                        'url': 'https://www.instagram.com/p/DB12345/',
                    }]
                }
            }
            with store.transaction() as db:
                Store.write(db, c)

            # 3. Simulate incoming Instagram webhook event
            ig_payload = {
                "object": "instagram",
                "entry": [
                    {
                        "id": "178414123456789",
                        "time": 1700000000,
                        "changes": [
                            {
                                "field": "comments",
                                "value": {
                                    "id": "ig_comment_12345",
                                    "text": "Is this tool completely free to join?",
                                    "from": {"id": "ig_user_777", "username": "dev_alex"},
                                    "media": {"id": "17999888777666"}
                                }
                            }
                        ]
                    }
                ]
            }
            raw_body = json.dumps(ig_payload).encode('utf-8')
            sig = 'sha256=' + hmac.new(app_secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()

            res = client.post('/api/webhooks/instagram', content=raw_body, headers={'x-hub-signature-256': sig})
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()['matched_comments'], 1)

            # 4. Check community inbox
            inbox = client.get('/api/engagement').json()
            self.assertEqual(len(inbox), 1)
            item = inbox[0]
            self.assertEqual(item['platform'], 'instagram')
            self.assertEqual(item['author'], 'dev_alex')
            self.assertEqual(item['text'], 'Is this tool completely free to join?')
            self.assertEqual(item['state'], 'QUEUED')

            # 5. Process draft reply
            community = app.state.community
            stepped = community.step()
            self.assertTrue(stepped)

            item_ready = client.get('/api/engagement').json()[0]
            self.assertEqual(item_ready['state'], 'AWAITING_APPROVAL')
            draft_hash = item_ready['draft_hash']

            # 6. Approve reply and post to Instagram
            mock_reply_resp = MagicMock()
            mock_reply_resp.status_code = 200
            mock_reply_resp.json.return_value = {'id': 'ig_reply_post_555'}

            with patch('httpx.post', return_value=mock_reply_resp) as mock_post:
                decide_res = client.post(f'/api/engagement/{item_ready["id"]}/decision', json={
                    'draft_hash': draft_hash,
                    'approve': True,
                })
                self.assertEqual(decide_res.status_code, 200)
                decided = decide_res.json()
                self.assertEqual(decided['state'], 'APPROVED')
                self.assertEqual(decided.get('instagram_reply_id'), 'ig_reply_post_555')
                self.assertTrue(decided.get('instagram_reply_posted'))
                self.assertTrue(mock_post.called)
                url_called = mock_post.call_args[0][0]
                self.assertIn('ig_comment_12345/replies', url_called)

    def test_instagram_detect_endpoint(self):
        app = create_app(self.tmp_path, start_worker=False)
        with TestClient(app) as client:
            settings = client.get('/api/settings').json()
            payload = {k: settings[k] for k in ('provider', 'model', 'brand', 'channel_settings', 'data_mode')}
            payload['social_keys'] = {
                'facebook_page_id': 'fb_page_888',
                'facebook_page_token': 'fb_token_888',
            }
            self.assertEqual(client.put('/api/settings', json=payload).status_code, 200)

            mock_graph_resp = MagicMock()
            mock_graph_resp.status_code = 200
            mock_graph_resp.json.return_value = {
                'name': 'My Brand Page',
                'instagram_business_account': {
                    'id': '178414999999999',
                    'username': 'mybrand_official',
                    'name': 'My Brand Official',
                    'profile_picture_url': 'https://scontent.cdn/pic.jpg',
                }
            }

            with patch('httpx.get', return_value=mock_graph_resp):
                detect_res = client.post('/api/integrations/instagram/detect')
                self.assertEqual(detect_res.status_code, 200)
                data = detect_res.json()
                self.assertTrue(data['connected'])
                self.assertEqual(data['account_id'], '178414999999999')
                self.assertEqual(data['username'], 'mybrand_official')


if __name__ == '__main__':
    unittest.main()
