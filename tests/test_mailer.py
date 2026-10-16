import unittest
from unittest.mock import MagicMock, patch
from app.mailer import MailerService, _base_email_template


class TestMailerService(unittest.TestCase):
    def setUp(self):
        self.mailer = MailerService(store=None)

    def test_base_email_template_rendering(self):
        html = _base_email_template(
            title="Test Email Title",
            preheader="Preview snippet",
            badge="Test Badge",
            content_html="<p>Test Content</p>",
            action_url="http://127.0.0.1:8000",
            action_label="Take Action"
        )
        self.assertIn("Test Email Title", html)
        self.assertIn("Preview snippet", html)
        self.assertIn("TEST BADGE", html.upper())
        self.assertIn("<p>Test Content</p>", html)
        self.assertIn("http://127.0.0.1:8000", html)
        self.assertIn("Take Action", html)

    def test_recipient_resolution_fallback(self):
        with patch.dict("os.environ", {"BREVO_RECIPIENT_EMAIL": "test_dest@example.com"}):
            recipients = self.mailer.get_recipients()
            self.assertEqual(recipients, ["test_dest@example.com"])

    def test_recipient_resolution_db_users(self):
        mock_store = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("user1@example.com",), ("user2@example.com",)]
        mock_store.reading.return_value.__enter__.return_value.execute.return_value = mock_cursor

        mailer_with_db = MailerService(store=mock_store)
        recipients = mailer_with_db.get_recipients()
        self.assertEqual(recipients, ["user1@example.com", "user2@example.com"])

    @patch("httpx.Client")
    def test_send_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.json.return_value = {"messageId": "<msg-1234@brevo>"}
        mock_client.__enter__.return_value.post.return_value = mock_resp
        mock_client_cls.return_value = mock_client

        with patch.dict("os.environ", {
            "BREVO_API_KEY": "xkeysib-mock-test-key",
            "BREVO_SENDER_NAME": "Ai-marketing-agent",
            "BREVO_SENDER_EMAIL": "vitabsquare@gmail.com",
            "BREVO_RECIPIENT_EMAIL": "vitabsquare@gmail.com",
        }):
            res = self.mailer.send(
                subject="Test Subject",
                html_content="<p>Hello World</p>",
                text_content="Hello World",
                recipients=["vitabsquare@gmail.com"]
            )
            self.assertTrue(res)
            mock_client.__enter__.return_value.post.assert_called_once()
            call_kwargs = mock_client.__enter__.return_value.post.call_args.kwargs
            self.assertEqual(call_kwargs["json"]["subject"], "Test Subject")
            self.assertEqual(call_kwargs["json"]["sender"]["email"], "vitabsquare@gmail.com")
            self.assertEqual(call_kwargs["json"]["to"], [{"email": "vitabsquare@gmail.com"}])

    def test_send_skipped_without_api_key(self):
        with patch.dict("os.environ", {"BREVO_API_KEY": ""}):
            res = self.mailer.send("Subject", "<p>hi</p>", "hi", ["test@example.com"])
            self.assertFalse(res)

    @patch("app.mailer.MailerService.send_async")
    def test_send_campaign_started(self, mock_send_async):
        campaign = {
            "brief": {"title": "Summer Launch", "goal": "Brand Awareness", "audience": "Gen Z"},
            "snapshot": {"configuration": {"destinations": [{"channel": "facebook"}, {"channel": "instagram"}]}}
        }
        self.mailer.send_campaign_started(campaign)
        mock_send_async.assert_called_once()
        subject, html, text = mock_send_async.call_args[0][:3]
        self.assertIn("Summer Launch", subject)
        self.assertIn("Summer Launch", html)
        self.assertIn("Brand Awareness", html)
        self.assertIn("FACEBOOK, INSTAGRAM", html)

    @patch("app.mailer.MailerService.send_async")
    def test_send_awaiting_approval(self, mock_send_async):
        campaign = {
            "brief": {"title": "Tech Conf Promo"},
            "results": {
                "writing": {
                    "output": {
                        "headline": "Unlock Tomorrow Today",
                        "destinations": {"facebook": "Join 5000+ engineers this fall."}
                    }
                }
            }
        }
        self.mailer.send_awaiting_approval(campaign)
        mock_send_async.assert_called_once()
        subject, html, text = mock_send_async.call_args[0][:3]
        self.assertIn("Approval Needed", subject)
        self.assertIn("Unlock Tomorrow Today", html)
        self.assertIn("Join 5000+ engineers this fall.", html)

    @patch("app.mailer.MailerService.send_async")
    def test_send_post_published(self, mock_send_async):
        campaign = {"brief": {"title": "Product Launch"}}
        receipts = [
            {"platform": "facebook", "url": "https://facebook.com/post/123", "status": "published"},
            {"platform": "twitter", "url": "https://x.com/post/456", "status": "published"}
        ]
        self.mailer.send_post_published(campaign, receipts)
        mock_send_async.assert_called_once()
        subject, html, text = mock_send_async.call_args[0][:3]
        self.assertIn("Product Launch", subject)
        self.assertIn("https://facebook.com/post/123", html)
        self.assertIn("https://x.com/post/456", html)

    @patch("app.mailer.MailerService.send_async")
    def test_send_comment_received(self, mock_send_async):
        item = {
            "author": "Alice Cooper",
            "text": "What is the price and shipping time?",
            "platform": "facebook"
        }
        self.mailer.send_comment_received(item)
        mock_send_async.assert_called_once()
        subject, html, text = mock_send_async.call_args[0][:3]
        self.assertIn("Alice Cooper", subject)
        self.assertIn("What is the price and shipping time?", html)

    @patch("app.mailer.MailerService.send_async")
    def test_send_reply_posted(self, mock_send_async):
        item = {
            "author": "Alice Cooper",
            "text": "What is the price?",
            "platform": "facebook",
            "event_id": "comm_123"
        }
        self.mailer.send_reply_posted(item, "Our service is completely free to start!", "fb_reply_999")
        mock_send_async.assert_called_once()
        subject, html, text = mock_send_async.call_args[0][:3]
        self.assertIn("Alice Cooper", subject)
        self.assertIn("completely free to start", html)
        self.assertIn("fb_reply_999", html)


if __name__ == "__main__":
    unittest.main()
