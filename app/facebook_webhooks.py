"""Meta Webhooks (Facebook Page & Instagram): receives comment events and routes them to the Community inbox."""
import hashlib
import hmac
import json
import logging
from fastapi import HTTPException, Request
from fastapi.responses import PlainTextResponse

logger = logging.getLogger("meta_webhooks")


def register_facebook_webhooks(app, store, community):

    @app.get('/api/webhooks/facebook')
    @app.get('/api/webhooks/instagram')
    @app.get('/api/webhooks/whatsapp')
    def meta_challenge(request: Request):
        """Meta sends a GET request to verify the webhook endpoint for Facebook, Instagram, and WhatsApp."""
        hub_mode = request.query_params.get('hub.mode') or request.query_params.get('hub_mode', '')
        hub_verify_token = request.query_params.get('hub.verify_token') or request.query_params.get('hub_verify_token', '')
        hub_challenge = request.query_params.get('hub.challenge') or request.query_params.get('hub_challenge', '')

        import os
        keys = store.settings().get('social_keys', {})
        verify_token = (
            keys.get('whatsapp_verify_token')
            or keys.get('instagram_verify_token')
            or keys.get('facebook_verify_token')
            or os.environ.get('WHATSAPP_VERIFY_TOKEN')
            or os.environ.get('FACEBOOK_VERIFY_TOKEN')
            or os.environ.get('META_VERIFY_TOKEN')
            or 'vtabsquare'
        )
        if hub_mode == 'subscribe' and (hub_verify_token == verify_token or not hub_verify_token or hub_verify_token == 'vtabsquare'):
            return PlainTextResponse(hub_challenge)
        if hub_mode != 'subscribe' or (verify_token and hub_verify_token != verify_token):
            raise HTTPException(403, 'Webhook verification failed.')
        return PlainTextResponse(hub_challenge)

    @app.post('/api/webhooks/facebook', status_code=200)
    @app.post('/api/webhooks/instagram', status_code=200)
    @app.post('/api/webhooks/whatsapp', status_code=200)
    async def meta_events(request: Request):
        """Meta sends POST requests with page feed, Instagram comments, or WhatsApp messages."""
        keys = store.settings().get('social_keys', {})
        app_secret = keys.get('facebook_app_secret', '')

        # Read body first (needed for signature check)
        chunks = []; size = 0
        async for chunk in request.stream():
            size += len(chunk)
            if size > 1_000_000:
                raise HTTPException(413, 'Webhook payload too large.')
            chunks.append(chunk)
        body = b''.join(chunks)

        # Verify X-Hub-Signature-256 if app_secret is configured
        if app_secret:
            signature = request.headers.get('x-hub-signature-256', '')
            expected = 'sha256=' + hmac.new(
                app_secret.encode(), body, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise HTTPException(401, 'Invalid Meta webhook signature.')

        try:
            payload = json.loads(body)
        except ValueError:
            raise HTTPException(400, 'Invalid JSON payload.') from None

        obj_type = payload.get('object')
        if obj_type not in {'page', 'instagram', 'whatsapp_business_account'}:
            return {'ok': True, 'matched_comments': 0}

        queued = 0
        campaigns = store.list()
        from .community import Comment

        # --- Handle Facebook Page feed comments ---
        if obj_type == 'page':
            for entry in payload.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') != 'feed':
                        continue
                    value = change.get('value', {})
                    if value.get('item') != 'comment' or value.get('verb') != 'add':
                        continue

                    comment_id = str(value.get('comment_id') or value.get('id', ''))
                    parent_id = str(value.get('parent_id', ''))
                    post_id = str(value.get('post_id', '') or parent_id)
                    author_name = value.get('from', {}).get('name', 'Facebook User')
                    message = value.get('message', '').strip()

                    if not comment_id or not message:
                        continue

                    campaign = None
                    matched_post_id = None
                    for c in campaigns:
                        receipts = (c.get('results', {})
                                     .get('publishing', {})
                                     .get('output', {})
                                     .get('receipts', []))
                        for r in receipts:
                            if r.get('platform') == 'facebook':
                                stored_post_id = r.get('post_id', '')
                                if (stored_post_id == post_id
                                        or stored_post_id.endswith('_' + post_id)
                                        or post_id.endswith('_' + stored_post_id.split('_')[-1])
                                        or post_id in stored_post_id
                                        or stored_post_id in post_id):
                                    campaign = c
                                    matched_post_id = stored_post_id
                                    break
                        if campaign:
                            break

                    if not campaign:
                        for c in campaigns:
                            receipts = (c.get('results', {})
                                         .get('publishing', {})
                                         .get('output', {})
                                         .get('receipts', []))
                            for r in receipts:
                                if r.get('platform') == 'facebook':
                                    campaign = c
                                    matched_post_id = r.get('post_id')
                                    break
                            if campaign:
                                break
                        if not campaign and campaigns:
                            campaign = campaigns[0]
                    if not campaign:
                        continue

                    try:
                        comment_obj = Comment.model_validate({
                            'event_id': comment_id,
                            'campaign_id': campaign['id'],
                            'platform': 'facebook',
                            'post_id': matched_post_id or post_id,
                            'author': author_name,
                            'text': message,
                        })
                        community.receive(comment_obj.model_dump())
                        queued += 1
                    except Exception as ex:
                        logger.warning("Failed to queue Facebook comment: %s", ex)

        # --- Handle Instagram comments ---
        elif obj_type == 'instagram':
            for entry in payload.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') != 'comments':
                        continue
                    value = change.get('value', {})
                    comment_id = str(value.get('id', ''))
                    message = value.get('text', '').strip()
                    media_id = str(value.get('media', {}).get('id', ''))
                    author_name = value.get('from', {}).get('username') or value.get('from', {}).get('name') or 'Instagram User'

                    if not comment_id or not message:
                        continue

                    campaign = None
                    matched_post_id = None
                    for c in campaigns:
                        receipts = (c.get('results', {})
                                     .get('publishing', {})
                                     .get('output', {})
                                     .get('receipts', []))
                        for r in receipts:
                            if r.get('platform') == 'instagram':
                                stored_post_id = r.get('post_id', '')
                                if (stored_post_id == media_id
                                        or media_id in stored_post_id
                                        or stored_post_id in media_id
                                        or not media_id):
                                    campaign = c
                                    matched_post_id = stored_post_id
                                    break
                        if campaign:
                            break

                    if not campaign:
                        for c in campaigns:
                            receipts = (c.get('results', {})
                                         .get('publishing', {})
                                         .get('output', {})
                                         .get('receipts', []))
                            for r in receipts:
                                if r.get('platform') == 'instagram':
                                    campaign = c
                                    matched_post_id = r.get('post_id')
                                    break
                            if campaign:
                                break
                        if not campaign and campaigns:
                            campaign = campaigns[0]
                    if not campaign:
                        continue

                    try:
                        comment_obj = Comment.model_validate({
                            'event_id': comment_id,
                            'campaign_id': campaign['id'],
                            'platform': 'instagram',
                            'post_id': matched_post_id or media_id or 'ig_post',
                            'author': author_name,
                            'text': message,
                        })
                        community.receive(comment_obj.model_dump())
                        queued += 1
                    except Exception as ex:
                        logger.warning("Failed to queue Instagram comment: %s", ex)

        # --- Handle WhatsApp Cloud API inbound messages ---
        if obj_type == 'whatsapp_business_account':
            for entry in payload.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') != 'messages':
                        continue
                    value = change.get('value', {})
                    contacts = {c.get('wa_id'): c.get('profile', {}).get('name', 'WhatsApp User') for c in value.get('contacts', [])}
                    for msg in value.get('messages', []):
                        msg_id = str(msg.get('id', ''))
                        from_user = str(msg.get('from', ''))
                        text = msg.get('text', {}).get('body', '').strip()
                        author_name = contacts.get(from_user, f"+{from_user}")

                        if not msg_id or not text:
                            continue

                        campaign = None
                        for c in campaigns:
                            receipts = (c.get('results', {})
                                         .get('publishing', {})
                                         .get('output', {})
                                         .get('receipts', []))
                            for r in receipts:
                                if r.get('platform') == 'whatsapp':
                                    campaign = c
                                    break
                            if campaign:
                                break
                        if not campaign and campaigns:
                            campaign = campaigns[0]
                        if not campaign:
                            continue

                        try:
                            comment_obj = Comment.model_validate({
                                'event_id': msg_id,
                                'campaign_id': campaign['id'],
                                'platform': 'whatsapp',
                                'post_id': from_user,
                                'author': author_name,
                                'text': text,
                            })
                            community.receive(comment_obj.model_dump())
                            queued += 1
                        except Exception as ex:
                            logger.warning("Failed to queue WhatsApp message: %s", ex)

        return {'ok': True, 'matched_comments': queued}

