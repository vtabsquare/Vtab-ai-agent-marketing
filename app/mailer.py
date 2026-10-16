"""Brevo (Sendinblue) transactional email notification service."""
import os
import json
import logging
import threading
from pathlib import Path
from typing import List, Optional, Dict, Any
import httpx

logger = logging.getLogger("mailer")
ROOT = Path(__file__).resolve().parents[1]


def _load_env_fallback():
    """Ensure .env is read if not loaded by parent process."""
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            var_name = name.strip()
            var_val = value.strip().strip('"').strip("'")
            if var_name:
                os.environ.setdefault(var_name, var_val)


_load_env_fallback()


def _base_email_template(title: str, preheader: str, badge: str, content_html: str, action_url: Optional[str] = None, action_label: Optional[str] = None) -> str:
    """Return a clean, modern, responsive HTML email template."""
    action_btn_html = ""
    if action_url and action_label:
        action_btn_html = f"""
        <div style="margin: 28px 0 10px; text-align: center;">
            <a href="{action_url}" style="background: linear-gradient(135deg, #6366f1, #4f46e5); color: #ffffff; text-decoration: none; padding: 13px 28px; font-weight: 600; font-size: 14px; border-radius: 8px; display: inline-block; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);">
                {action_label} &rarr;
            </a>
        </div>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f3f4f6;">
    <div style="display: none; max-height: 0px; overflow: hidden;">{preheader}</div>
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0b0f19; padding: 35px 15px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" style="max-width: 580px; background-color: #111827; border: 1px solid #1f2937; border-radius: 14px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 28px 32px; background: linear-gradient(135deg, #1e1b4b 0%, #172554 100%); border-bottom: 1px solid #374151;">
                            <div style="display: inline-block; padding: 4px 12px; background: rgba(99, 102, 241, 0.25); border: 1px solid #6366f1; border-radius: 9999px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; color: #a5b4fc; text-transform: uppercase;">
                                {badge}
                            </div>
                            <h1 style="margin: 14px 0 0; font-size: 22px; font-weight: 700; color: #ffffff; line-height: 1.3;">
                                {title}
                            </h1>
                        </td>
                    </tr>
                    <!-- Body Content -->
                    <tr>
                        <td style="padding: 32px; font-size: 14px; line-height: 1.65; color: #d1d5db;">
                            {content_html}
                            {action_btn_html}
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 32px; background-color: #0f172a; border-top: 1px solid #1f2937; text-align: center; font-size: 12px; color: #9ca3af;">
                            <p style="margin: 0;">AI Marketing Manager &bull; Autonomous Brand & Community Pipeline</p>
                            <p style="margin: 6px 0 0; font-size: 11px; color: #6b7280;">Notification generated automatically via Brevo.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


class MailerService:
    API_URL = "https://api.brevo.com/v3/smtp/email"

    def __init__(self, store=None):
        self.store = store

    @property
    def api_key(self) -> str:
        return os.environ.get("BREVO_API_KEY", "").strip()

    @property
    def sender_name(self) -> str:
        return os.environ.get("BREVO_SENDER_NAME", "Ai-marketing-agent").strip()

    @property
    def sender_email(self) -> str:
        return os.environ.get("BREVO_SENDER_EMAIL", "vitabsquare@gmail.com").strip()

    def get_recipients(self) -> List[str]:
        """Resolve recipient email addresses from workspace users or environment fallback."""
        recipients = []
        if self.store:
            try:
                with self.store.reading() as db:
                    rows = db.execute("SELECT email FROM users WHERE active = 1").fetchall()
                    for r in rows:
                        email = str(r[0]).strip()
                        if "@" in email and email not in recipients:
                            recipients.append(email)
            except Exception as e:
                logger.warning("Failed to query workspace users for email recipients: %s", e)

        # Fallback to configured recipient or sender
        if not recipients:
            env_recipient = os.environ.get("BREVO_RECIPIENT_EMAIL", "").strip()
            if env_recipient and "@" in env_recipient:
                recipients.append(env_recipient)
            elif self.sender_email and "@" in self.sender_email:
                recipients.append(self.sender_email)

        return recipients

    def send(self, subject: str, html_content: str, text_content: str, recipients: Optional[List[str]] = None) -> bool:
        """Synchronously send an email using Brevo v3 API."""
        key = self.api_key
        if not key:
            logger.warning("Brevo API key not set; skipping email notification: %s", subject)
            return False

        to_list = recipients or self.get_recipients()
        if not to_list:
            logger.warning("No recipient found for email notification: %s", subject)
            return False

        payload = {
            "sender": {"name": self.sender_name, "email": self.sender_email},
            "to": [{"email": email} for email in to_list],
            "subject": subject,
            "htmlContent": html_content,
            "textContent": text_content,
        }

        headers = {
            "api-key": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            with httpx.Client(timeout=20.0) as client:
                resp = client.post(self.API_URL, json=payload, headers=headers)
                if resp.status_code in {200, 201, 202}:
                    logger.info("Sent email '%s' via Brevo to %s (messageId: %s)", subject, to_list, resp.json().get("messageId"))
                    return True
                else:
                    logger.error("Brevo API returned error %s: %s", resp.status_code, resp.text)
                    return False
        except Exception as e:
            logger.error("Failed to send Brevo email: %s", e)
            return False

    def send_async(self, subject: str, html_content: str, text_content: str, recipients: Optional[List[str]] = None):
        """Dispatch email in background thread to avoid blocking caller."""
        thread = threading.Thread(
            target=self.send,
            args=(subject, html_content, text_content, recipients),
            daemon=True,
            name="brevo-mailer-worker",
        )
        thread.start()

    # -------------------------------------------------------------------------
    # Lifecycle Email Notifications
    # -------------------------------------------------------------------------

    def send_campaign_started(self, campaign: Dict[str, Any]):
        """Trigger 1: Sent when bot campaign workflow starts."""
        brief = campaign.get("brief", {})
        title = brief.get("title") or "New Campaign"
        audience = brief.get("audience") or "Target Audience"
        goal = brief.get("goal") or "Brand awareness"
        destinations = [d.get("channel") for d in campaign.get("snapshot", {}).get("configuration", {}).get("destinations", [])]
        dest_str = ", ".join(destinations).upper() if destinations else "SOCIAL CHANNELS"

        subject = f"🚀 [Campaign Started] {title}"
        preheader = f"AI bots have started research and strategy generation for {title}."

        content_html = f"""
        <p style="margin-top: 0;">The AI Marketing bot team has officially kicked off execution for <strong>{title}</strong>.</p>
        <div style="background-color: #1f2937; border-left: 4px solid #6366f1; padding: 14px 18px; margin: 20px 0; border-radius: 6px;">
            <p style="margin: 0 0 6px;"><strong>Goal:</strong> {goal}</p>
            <p style="margin: 0 0 6px;"><strong>Target Audience:</strong> {audience}</p>
            <p style="margin: 0;"><strong>Destinations:</strong> {dest_str}</p>
        </div>
        <p>The <strong>Researcher Bot</strong> and <strong>Strategist Bot</strong> are analyzing brand constraints and factual records. We will notify you as soon as the copy and visuals are ready for your review.</p>
        """

        text_content = f"Campaign Started: {title}\nGoal: {goal}\nAudience: {audience}\nDestinations: {dest_str}\n\nAI bots are working on research and strategy."
        dashboard_url = os.environ.get("MARKETING_DASHBOARD_URL", "http://127.0.0.1:8000")
        html = _base_email_template(
            title=f"Campaign Started: {title}",
            preheader=preheader,
            badge="Campaign Kickoff",
            content_html=content_html,
            action_url=dashboard_url,
            action_label="Open Workspace",
        )
        self.send_async(subject, html, text_content)

    def send_awaiting_approval(self, campaign: Dict[str, Any]):
        """Trigger 2: Sent when bot fully ran and requires human approval."""
        brief = campaign.get("brief", {})
        title = brief.get("title") or "Campaign"
        results = campaign.get("results", {})
        writing_out = results.get("writing", {}).get("output", {})
        headline = writing_out.get("headline") or writing_out.get("core_message") or "Draft Copy"
        dest_copy = writing_out.get("destinations", {})
        sample_copy = next(iter(dest_copy.values()), "") if dest_copy else writing_out.get("message", "")
        if len(sample_copy) > 280:
            sample_copy = sample_copy[:280] + "..."

        subject = f"⚡ [Approval Needed] {title} is Ready for Review"
        preheader = f"Manager Bot has prepared {title} and awaits your authorization to publish."

        content_html = f"""
        <p style="margin-top: 0;">The content creation pipeline is complete! <strong>Manager Bot</strong> has reviewed the package and is waiting for your authorization before publishing live.</p>
        <div style="background-color: #1f2937; border-radius: 8px; padding: 18px; margin: 20px 0; border: 1px solid #374151;">
            <p style="margin: 0 0 8px; font-size: 16px; font-weight: 700; color: #ffffff;">{headline}</p>
            <blockquote style="margin: 0; padding-left: 14px; border-left: 3px solid #10b981; font-style: italic; color: #e5e7eb;">
                "{sample_copy}"
            </blockquote>
        </div>
        <p>Please review the creative asset, destination variants, and brand validation in your dashboard to approve or request revisions.</p>
        """

        text_content = f"Approval Needed for {title}\nHeadline: {headline}\nPreview: {sample_copy}\n\nPlease visit the dashboard to approve or revise."
        dashboard_url = os.environ.get("MARKETING_DASHBOARD_URL", "http://127.0.0.1:8000")
        html = _base_email_template(
            title=f"Review & Approve: {title}",
            preheader=preheader,
            badge="Action Required",
            content_html=content_html,
            action_url=dashboard_url,
            action_label="Review and Approve in Dashboard",
        )
        self.send_async(subject, html, text_content)

    def send_post_published(self, campaign: Dict[str, Any], receipts: List[Dict[str, Any]]):
        """Trigger 3: Sent when content is published to social handles."""
        brief = campaign.get("brief", {})
        title = brief.get("title") or "Campaign"

        links_html = ""
        links_text = ""
        for r in receipts:
            platform = r.get("platform", "Social").capitalize()
            url = r.get("url")
            status = r.get("status", "published")
            if url:
                links_html += f'<li style="margin-bottom: 8px;"><strong>{platform}:</strong> <a href="{url}" style="color: #60a5fa; text-decoration: underline;">View Live Post &rarr;</a></li>'
                links_text += f"\n- {platform}: {url}"
            else:
                links_html += f'<li style="margin-bottom: 8px;"><strong>{platform}:</strong> Status: {status} (ID: {r.get("post_id")})</li>'
                links_text += f"\n- {platform}: {status} (ID: {r.get('post_id')})"

        subject = f"🎉 [Published] {title} is Live on Social Handles!"
        preheader = f"Your campaign has been successfully published to your connected social channels."

        content_html = f"""
        <p style="margin-top: 0;">Great news! <strong>Publisher Bot</strong> has successfully distributed <strong>{title}</strong> to your authorized social media destinations.</p>
        <div style="background-color: #1f2937; border-radius: 8px; padding: 18px; margin: 20px 0; border: 1px solid #374151;">
            <p style="margin: 0 0 10px; font-weight: 700; color: #10b981;">Confirmed Live Channels:</p>
            <ul style="margin: 0; padding-left: 20px; color: #e5e7eb;">
                {links_html}
            </ul>
        </div>
        <p>Engagement monitoring is active. Whenever users comment or enquire on your posts, Community Bot will notify you and draft brand-aligned responses.</p>
        """

        text_content = f"Published: {title}\n\nConfirmed Channels:{links_text}\n\nLive on social handles!"
        dashboard_url = os.environ.get("MARKETING_DASHBOARD_URL", "http://127.0.0.1:8000")
        html = _base_email_template(
            title=f"Published Live: {title}",
            preheader=preheader,
            badge="Post Published",
            content_html=content_html,
            action_url=dashboard_url,
            action_label="Open Dashboard",
        )
        self.send_async(subject, html, text_content)

    def send_comment_received(self, item: Dict[str, Any]):
        """Trigger 4a: Sent when a customer comment arrives."""
        author = item.get("author", "A customer")
        text = item.get("text", "")
        platform = item.get("platform", "facebook").capitalize()

        subject = f"💬 [New Customer Comment] from {author} on {platform}"
        preheader = f"{author} commented on your {platform} post: '{text[:60]}...'"

        content_html = f"""
        <p style="margin-top: 0;">A new comment was posted on your <strong>{platform}</strong> page:</p>
        <div style="background-color: #1f2937; border-left: 4px solid #3b82f6; padding: 16px; margin: 20px 0; border-radius: 6px;">
            <p style="margin: 0 0 6px; font-weight: 700; color: #ffffff;">{author}:</p>
            <blockquote style="margin: 0; color: #e5e7eb; font-style: italic;">
                "{text}"
            </blockquote>
        </div>
        <p><strong>Community Bot</strong> is drafting a brand-aligned reply based on your approved facts. Check your Community inbox to review and approve the reply.</p>
        """

        text_content = f"New Comment from {author} on {platform}:\n\"{text}\"\n\nCommunity Bot is drafting a reply."
        dashboard_url = os.environ.get("MARKETING_DASHBOARD_URL", "http://127.0.0.1:8000")
        html = _base_email_template(
            title=f"New Comment on {platform}",
            preheader=preheader,
            badge="Community Engagement",
            content_html=content_html,
            action_url=dashboard_url,
            action_label="View in Community Inbox",
        )
        self.send_async(subject, html, text_content)

    def send_reply_posted(self, item: Dict[str, Any], reply_text: str, reply_id: Optional[str] = None):
        """Trigger 4b: Sent when a community reply is approved and published back to the social thread."""
        author = item.get("author", "Customer")
        platform = item.get("platform", "facebook").capitalize()

        subject = f"✅ [Reply Published] to {author} on {platform}"
        preheader = f"Your approved reply has been posted to {author}'s comment on {platform}."

        content_html = f"""
        <p style="margin-top: 0;">Your approved Community Bot response has been successfully published to the discussion thread on <strong>{platform}</strong>.</p>
        <div style="background-color: #1f2937; border-radius: 8px; padding: 18px; margin: 20px 0; border: 1px solid #374151;">
            <p style="margin: 0 0 8px; font-size: 12px; color: #9ca3af; text-transform: uppercase; font-weight: 700;">In Reply to {author}:</p>
            <p style="margin: 0 0 14px; font-style: italic; color: #9ca3af;">"{item.get('text', '')}"</p>
            <div style="border-top: 1px solid #374151; padding-top: 12px;">
                <p style="margin: 0 0 6px; font-size: 12px; color: #10b981; font-weight: 700; text-transform: uppercase;">Published Reply:</p>
                <p style="margin: 0; color: #ffffff; font-weight: 500;">"{reply_text}"</p>
            </div>
        </div>
        <p style="font-size: 13px; color: #9ca3af;">Thread identifier: <code>{reply_id or item.get('event_id')}</code></p>
        """

        text_content = f"Reply Published on {platform} to {author}:\n\nYour Reply: \"{reply_text}\""
        dashboard_url = os.environ.get("MARKETING_DASHBOARD_URL", "http://127.0.0.1:8000")
        html = _base_email_template(
            title=f"Reply Live on {platform}",
            preheader=preheader,
            badge="Reply Confirmed",
            content_html=content_html,
            action_url=dashboard_url,
            action_label="Open Community Inbox",
        )
        self.send_async(subject, html, text_content)
