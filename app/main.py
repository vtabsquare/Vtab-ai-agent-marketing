import json
import base64
import hashlib
import hmac
import time
import secrets
import os
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .community import Community, Comment, ReplyDecision
from .agents import AgentRegistry
from .contracts import Brief, SettingsInput, Decision, Revision, Strategy, InputAnswer, WebsiteScanRequest, KnowledgeDecision, CatalogItemInput, AudienceInput, LeadInput, LeadUpdate, LeadImportRequest, MemoryInput, MemoryDecision, LandingPageInput, UTMRequest, MetricEventInput, ExperimentInput, ExperimentResultInput, ConnectorSyncInput, ConnectorWriteInput, LoginInput, WorkspaceUserInput, UserStateInput
from .controller import Controller, STAGES, fingerprint
from .providers import build_provider, get_key, ModelRequest, ProviderError
from .store import Store, Conflict, Missing
from .tools import brand_card
from .capabilities import effective_capabilities, normalize_settings
from .website import WebsiteIntelligence
from .standalone import StandaloneWorkspace
from .memory import MemoryService
from .workflow_registry import WorkflowRegistry
from .conversion import ConversionService
from .analytics import AnalyticsService
from .connectors import ConnectorService
from .operations import OperationsService, ROLE_DESCRIPTIONS

ROOT = Path(__file__).resolve().parents[1]


def create_app(data_dir=None, start_worker=True):
    store = Store(data_dir or os.environ.get("MARKETING_DATA_DIR", str(ROOT / "data")))
    registry = AgentRegistry(ROOT)
    workflow_registry = WorkflowRegistry(ROOT)
    from .mailer import MailerService
    mailer = MailerService(store)
    controller = Controller(store, registry, workflow_registry, mailer=mailer)
    community = Community(store, registry, mailer=mailer)
    website = WebsiteIntelligence(store)
    standalone = StandaloneWorkspace(store)
    memory = MemoryService(store)
    conversion = ConversionService(store)
    analytics_service = AnalyticsService(store)
    connectors = ConnectorService(store)
    operations = OperationsService(store)
    server = os.environ.get('MARKETING_MODE', 'local') == 'server'
    password = os.environ.get('MARKETING_ADMIN_PASSWORD', '')
    if server and len(password)<16:
        raise RuntimeError('Server mode requires MARKETING_ADMIN_PASSWORD with at least 16 characters.')
    if server: operations.bootstrap_owner(password)
    controller.demo_delay = 0.65 if start_worker else 0
    stop = threading.Event()

    def worker():
        while not stop.is_set():
            try:
                active = controller.step()
                active = community.step() or active
            except Exception:
                # No raw exception/request text in logs: it could contain provider credentials.
                active = False
            stop.wait(0.3 if active else 0.8)

    @asynccontextmanager
    async def lifespan(app):
        threads = []
        if start_worker:
            for index in range(4):
                thread = threading.Thread(target=worker, name=f"bot-worker-{index+1}", daemon=True)
                thread.start()
                threads.append(thread)
        yield
        stop.set()
        for thread in threads:
            thread.join(timeout=2)
        if not any(thread.is_alive() for thread in threads):
            store.close()

    app = FastAPI(title="AI Marketing Manager", lifespan=lifespan)
    app.state.community = community
    from .x_webhooks import register_x_webhooks
    register_x_webhooks(app, store, community)
    from .facebook_webhooks import register_facebook_webhooks
    register_facebook_webhooks(app, store, community)
    app.state.store, app.state.controller = store, controller
    app.state.operations = operations
    app.state.mailer = mailer
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=os.environ.get("MARKETING_ALLOWED_HOSTS", "localhost,127.0.0.1,testserver,*.trycloudflare.com,*.ngrok-free.app,*.ngrok.io,*").split(","))

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # Default validation responses can echo submitted keys or private form values.
        return JSONResponse({"detail": "Please check the form fields and try again.",
                             "fields": [list(error["loc"]) for error in exc.errors()]}, status_code=422)

    @app.middleware("http")
    async def local_guard(request: Request, call_next):
        public_path=request.url.path.startswith('/forms/') or request.url.path.startswith('/public/forms/') or request.url.path=='/api/public/events'
        auth_public=request.url.path in {'/api/health','/api/auth/login','/api/webhooks/engagement','/api/webhooks/x','/api/webhooks/facebook','/api/webhooks/instagram','/api/webhooks/whatsapp'}
        actor=None if server else {'id':'local-owner','email':'local-owner','name':'Local workspace owner','role':'owner','active':True}
        session_token=request.cookies.get('marketing_session','')
        if server and not auth_public and not public_path:
            actor=operations.session_user(session_token)
            authorization=request.headers.get('authorization','')
            try:
                scheme,encoded=authorization.split(' ',1)
                username,supplied=base64.b64decode(encoded,validate=True).decode().split(':',1)
                valid=scheme.lower()=='basic' and secrets.compare_digest(username,'admin') and secrets.compare_digest(supplied,password)
            except Exception: valid=False
            if valid:
                actor=next((item for item in operations.users() if item['role']=='owner' and item['active']),actor)
            if not actor:
                return JSONResponse({'detail':'Sign in to your marketing workspace.'},status_code=401,headers={'WWW-Authenticate':'Basic realm="Marketing workspace"'})
        request.state.actor=actor or {'id':'anonymous','email':'anonymous','role':'none'}
        if server and actor and request.method not in {'GET','HEAD','OPTIONS'}:
            restricted=request.url.path.startswith(('/api/users','/api/audit','/api/backup','/api/diagnostics')) or request.url.path=='/api/settings'
            if actor['role'] in {'viewer','analyst'} or (actor['role']=='editor' and restricted):
                return JSONResponse({'detail':'Your workspace role does not allow this action.'},status_code=403)
        if server and actor and request.method=='GET' and request.url.path.startswith(('/api/users','/api/audit','/api/backup')) and actor['role'] not in {'owner','admin'}:
            return JSONResponse({'detail':'Your workspace role does not allow this view.'},status_code=403)
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            if origin:
                origin_clean = origin.rstrip("/")
                host = request.headers.get("host", "")
                current_host = host.split(":")[0].lower() if host else ""
                origin_host = origin_clean.split("://")[-1].split(":")[0].lower() if "://" in origin_clean else origin_clean.lower()

                port = os.environ.get('PORT', os.environ.get('MARKETING_PORT', '8000'))
                allowed = {
                    f"http://127.0.0.1:{port}",
                    f"http://localhost:{port}",
                    "http://127.0.0.1:8000",
                    "http://localhost:8000",
                    "http://127.0.0.1:5173",
                    "http://localhost:5173",
                }
                if host:
                    allowed.add(f"http://{host}")
                    allowed.add(f"https://{host}")
                render_url = os.environ.get("RENDER_EXTERNAL_URL")
                if render_url:
                    allowed.add(render_url.rstrip("/"))
                allowed.update(filter(None, os.environ.get('MARKETING_ALLOWED_ORIGINS', '').split(',')))

                is_allowed = (
                    origin_clean in allowed
                    or (current_host and origin_host == current_host)
                    or origin_host.endswith(".onrender.com")
                    or origin_host.endswith(".render.com")
                )
                if not is_allowed:
                    return JSONResponse({"detail": "This workspace only accepts actions from its configured browser origin."}, status_code=403)
        try:
            response = await call_next(request)
        except Exception:
            response = JSONResponse({'detail':'The server could not finish this request. Please retry. Your saved workflows are retained.'}, status_code=500)
        try:
            if request.url.path.startswith('/api/') and not public_path:
                operations.audit(request.state.actor,request,response.status_code)
        except Exception:
            pass
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    def perform(fn):
        try:
            return fn()
        except Missing as exc:
            raise HTTPException(404, str(exc)) from None
        except Conflict as exc:
            raise HTTPException(409, str(exc)) from None
        except ProviderError as exc:
            raise HTTPException(400, str(exc)) from None

    def public_settings():
        s = store.settings()
        key = get_key(store)
        s['configured_integrations']={k:bool(v) for k,v in s.pop('social_keys',{}).items()}
        s['social_keys']={}
        s['deployment_mode']='server' if server else 'local'
        s["has_api_key"] = bool(key)
        s["ready"] = s["provider"] == "demo" or s.get("tested_fingerprint") == fingerprint(s, key)
        s["tested_fingerprint"] = ""  # Never expose credential-derived fingerprint.
        s["environment_model"] = os.environ.get("GEMINI_MODEL", "")
        return s

    @app.get("/api/health")
    def health():
        return {"status": "ok", "application": "marketing-manager", "mode": "server" if server else "local", "publishing": store.settings().get('publishing_mode','simulation')}

    @app.post('/api/auth/login')
    def login(data: LoginInput):
        if not server: return {'user':{'id':'local-owner','email':'local-owner','name':'Local workspace owner','role':'owner','active':True},'mode':'local'}
        result=operations.authenticate(data.email,data.password)
        if not result: raise HTTPException(401,'The email or password is incorrect.')
        user,token=result
        response=JSONResponse({'user':user,'roles':ROLE_DESCRIPTIONS})
        response.set_cookie('marketing_session',token,max_age=operations.SESSION_TTL,httponly=True,
                            secure=os.environ.get('MARKETING_COOKIE_SECURE','true').lower()=='true',samesite='strict',path='/')
        return response

    @app.post('/api/auth/logout')
    def logout(request: Request):
        operations.logout(request.cookies.get('marketing_session',''))
        response=JSONResponse({'signed_out':True}); response.delete_cookie('marketing_session',path='/')
        return response

    @app.get('/api/auth/me')
    def auth_me(request: Request): return {'user':request.state.actor,'roles':ROLE_DESCRIPTIONS}

    @app.get('/api/users')
    def workspace_users(): return operations.users()

    @app.post('/api/users',status_code=201)
    def create_workspace_user(data: WorkspaceUserInput,request: Request):
        return perform(lambda:operations.create_user(data.model_dump(),request.state.actor))

    @app.put('/api/users/{user_id}')
    def update_workspace_user(user_id: str,data: UserStateInput,request: Request):
        return perform(lambda:operations.update_user(user_id,data.model_dump(),request.state.actor))

    @app.get('/api/audit')
    def audit_events(limit: int=200): return operations.audit_events(limit)

    @app.get('/api/diagnostics')
    def diagnostics(): return operations.diagnostics()

    @app.post('/api/backup')
    def backup():
        path=perform(operations.backup)
        return FileResponse(path,media_type='application/zip',filename=path.name)

    @app.get('/api/notifications')
    def notifications():
        items = []
        for c in store.list():
            if c['state'] in {'CANCELLED', 'COMPLETED'}:
                continue
            for q in c['input_requests']:
                if q['status'] == 'OPEN':
                    items.append({**q, 'campaign_id': c['id'], 'workflow': c['brief']['title']})
            for role, node in c['nodes'].items():
                if node['state'] == 'BLOCKED':
                    items.append({'id': c['id']+role, 'campaign_id': c['id'], 'workflow': c['brief']['title'],
                                  'role': role, 'kind': 'attention', 'question': node['error']['message'],
                                  'status': 'OPEN', 'created_at': c['updated_at']})
        return sorted(items, key=lambda item: item['created_at'], reverse=True)

    @app.get("/api/settings")
    def settings():
        return public_settings()

    @app.get('/api/capabilities')
    def capabilities():
        return effective_capabilities(store.settings())

    @app.get('/api/workflow-definitions')
    def workflow_definitions():
        return workflow_registry.available(effective_capabilities(store.settings())['capabilities'])

    @app.post('/api/website/scan')
    def scan_website(data: WebsiteScanRequest):
        return perform(lambda:website.scan(data.url,data.max_pages))

    @app.get('/api/knowledge')
    def knowledge(status: str | None=None):
        if status and status not in {'discovered','approved','rejected','superseded'}:
            raise HTTPException(422,'Unknown knowledge status.')
        return store.knowledge(status)

    @app.post('/api/knowledge/{item_id}/decision')
    def decide_knowledge(item_id: str,data: KnowledgeDecision):
        return perform(lambda:store.decide_knowledge(item_id,data.status,data.note))

    @app.get('/api/catalog')
    def catalog(): return store.list_records('catalog_items')

    @app.post('/api/catalog',status_code=201)
    def create_catalog_item(data: CatalogItemInput): return store.create_record('catalog_items',data.model_dump())

    @app.get('/api/audiences')
    def audiences(): return store.list_records('audiences')

    @app.post('/api/audiences',status_code=201)
    def create_audience(data: AudienceInput): return store.create_record('audiences',data.model_dump())

    @app.get('/api/leads')
    def leads(): return store.leads()

    @app.post('/api/leads',status_code=201)
    def create_lead(data: LeadInput): return perform(lambda:store.create_lead(data.model_dump()))

    @app.put('/api/leads/{lead_id}')
    def update_lead(lead_id: str,data: LeadUpdate): return perform(lambda:store.update_lead(lead_id,data.model_dump()))

    @app.delete('/api/leads/{lead_id}')
    def delete_lead(lead_id: str): return perform(lambda:store.delete_lead(lead_id))

    @app.post('/api/imports/leads')
    def import_leads(data: LeadImportRequest): return perform(lambda:standalone.import_leads(data.csv_text,data.mapping,data.source))

    @app.get('/api/leads/export')
    def export_leads():
        return Response(json.dumps(store.leads(),indent=2),media_type='application/json',
                        headers={'Content-Disposition':'attachment; filename="leads.json"'})

    @app.get('/api/memories')
    def memories(status: str | None=None,scope: str | None=None): return memory.list(status,scope)

    @app.post('/api/memories',status_code=201)
    def create_memory(data: MemoryInput): return perform(lambda:memory.create(data.model_dump()))

    @app.post('/api/memories/{memory_id}/decision')
    def decide_memory(memory_id: str,data: MemoryDecision): return perform(lambda:memory.decide(memory_id,data.status,data.note))

    @app.delete('/api/memories/{memory_id}')
    def delete_memory(memory_id: str): return perform(lambda:memory.delete(memory_id))

    @app.get('/api/landing-pages')
    def landing_pages(): return conversion.list_pages()

    @app.post('/api/landing-pages',status_code=201)
    def create_landing_page(data: LandingPageInput): return perform(lambda:conversion.create_page(data.model_dump()))

    @app.post('/api/landing-pages/{page_id}/publish')
    def publish_landing_page(page_id: str): return perform(lambda:conversion.publish(page_id))

    @app.post('/api/utm')
    def build_utm(data: UTMRequest): return perform(lambda:{'url':conversion.utm_url(data.url,data.source,data.medium,data.campaign,data.content)})

    @app.get('/forms/{slug}')
    def public_landing_page(slug: str):
        page=perform(lambda:conversion.get_public(slug)); conversion.event('page_view','landing_page',page.get('campaign_id'),{'slug':slug})
        return Response(conversion.render(page),media_type='text/html')

    @app.post('/public/forms/{token}/submit')
    async def public_form_submit(token: str,request: Request):
        from urllib.parse import parse_qs
        page=perform(lambda:conversion.get_by_token(token)); body=await request.body()
        if len(body)>16000: raise HTTPException(413,'Lead form is too large.')
        form={key:values[-1] for key,values in parse_qs(body.decode('utf-8','replace'),keep_blank_values=True).items()}
        if form.get('website'): return {'accepted':True}
        consent='granted' if form.get('consent')=='granted' else 'denied'
        lead=perform(lambda:store.create_lead({'name':str(form.get('name',''))[:200],'email':str(form.get('email',''))[:320],
            'phone':str(form.get('phone',''))[:80],'source':'landing_page:'+page['slug'],'campaign_id':page.get('campaign_id'),
            'product_interest':page.get('product_interest',''),'message':str(form.get('message',''))[:4000],
            'consent_status':consent,'custom_fields':{}}))
        conversion.event('form_submit','landing_page',page.get('campaign_id'),{'lead_id':lead['id'],'slug':page['slug']})
        return {'accepted':True,'lead_id':lead['id']}

    @app.post('/api/public/events',status_code=202)
    def public_event(data: MetricEventInput): return conversion.event(data.event_type,data.source,data.campaign_id,data.metadata)

    @app.get('/api/analytics/funnel')
    def funnel(campaign_id: str | None=None): return analytics_service.funnel(campaign_id)

    @app.get('/api/experiments')
    def experiments(): return analytics_service.experiments()

    @app.post('/api/experiments',status_code=201)
    def create_experiment(data: ExperimentInput): return perform(lambda:analytics_service.create_experiment(data.model_dump()))

    @app.post('/api/experiments/{experiment_id}/results')
    def record_experiment(experiment_id: str,data: ExperimentResultInput): return perform(lambda:analytics_service.record(experiment_id,data.model_dump()))

    @app.post('/api/experiments/{experiment_id}/complete')
    def complete_experiment(experiment_id: str): return perform(lambda:analytics_service.close(experiment_id))

    @app.get('/api/connector-types')
    def connector_types(): return connectors.types()

    @app.post('/api/connectors/{connector_id}/sync')
    def sync_connector(connector_id: str,data: ConnectorSyncInput):
        return perform(lambda:connectors.sync(connector_id,[record.model_dump() for record in data.records],data.cursor))

    @app.get('/api/connectors/{connector_id}/records')
    def connector_records(connector_id: str,entity_type: str | None=None): return perform(lambda:connectors.records(connector_id,entity_type))

    @app.post('/api/connectors/{connector_id}/outbox',status_code=202)
    def connector_write(connector_id: str,data: ConnectorWriteInput):
        return perform(lambda:connectors.queue_write(connector_id,data.entity_type,data.external_id,data.operation,data.fields,data.approved_by))

    @app.put("/api/settings")
    def save_settings(data: SettingsInput):
        settings = normalize_settings(data.model_dump(exclude={"api_key"}))
        old = store.settings()
        for field in ('configuration_version','data_mode','website_url','data_sources','connectors','lead_destination','channel_settings','feature_flags'):
            if field not in data.model_fields_set: settings[field]=old.get(field,settings[field])
        if settings["provider"] == "demo":
            settings["model"] = "deterministic-demo-v1"
        elif not settings["model"]:
            raise HTTPException(400, "Enter a Gemini model identifier.")
        known = {
            'discord_webhook', 'twitter_access_token', 'twitter_api_key', 'twitter_api_secret', 'twitter_client_secret',
            'linkedin_token', 'linkedin_author', 'hf_token',
            'facebook_page_id', 'facebook_page_token', 'facebook_app_secret', 'facebook_verify_token',
            'instagram_account_id', 'instagram_access_token', 'instagram_verify_token',
            'whatsapp_phone_number_id', 'whatsapp_token', 'whatsapp_recipient',
        }
        if set(settings['social_keys'])-known or any(len(v)>2000 for v in settings['social_keys'].values()):
            raise HTTPException(422,'Check your integration fields.')
        settings['social_keys']={**old.get('social_keys',{}),**settings['social_keys']}
        publishing_channels=[name for name,item in settings.get('channel_settings', {}).items()
                             if item.get('mode') in {'publishing_connected','fully_connected'}]
        if publishing_channels: settings['platforms']=publishing_channels

        key = data.api_key.strip() if data.api_key is not None else get_key(store)
        settings["tested_fingerprint"] = old.get("tested_fingerprint", "") if fingerprint(old, get_key(store)) == fingerprint(settings, key) else ""
        store.set_settings(settings, key=data.api_key.strip() if data.api_key is not None else None)
        return public_settings()

    @app.post("/api/settings/test")
    def test_configuration():
        s = store.settings()
        key = get_key(store)
        provider = perform(lambda: build_provider(s, key))
        result = perform(lambda: provider.generate(ModelRequest("strategy", {"brand": s["brand"], "brief": {"audience": "local test audience", "goal": "Connection test"}}, Strategy, "connection-test.v1")))
        # Do not mark a concurrently changed configuration tested.
        current = store.settings()
        if fingerprint(current, get_key(store)) != fingerprint(s, key):
            raise HTTPException(409, "Configuration changed while the test was running. Test again.")
        current["tested_fingerprint"] = fingerprint(s, key)
        store.set_settings(current)
        return {"ok": True, "message": "Connection and structured output test passed.", "provider": provider.name, "model": provider.model}

    @app.post("/api/notifications/test-email")
    def send_test_email():
        recipients = mailer.get_recipients()
        if not recipients:
            raise HTTPException(400, "No email recipient configured or found.")
        success = mailer.send(
            subject="🧪 [Test Notification] Brevo Email Service Connected",
            html_content="""<div style="font-family:sans-serif;background:#0b0f19;color:#fff;padding:24px;border-radius:8px;">
                <h2 style="color:#6366f1;">Brevo Email Service Active</h2>
                <p>This is a test notification confirming your Brevo transactional email configuration is working properly.</p>
                <p style="color:#9ca3af;font-size:12px;">Sender: Ai-marketing-agent &lt;vitabsquare@gmail.com&gt;</p>
            </div>""",
            text_content="Brevo Email Service Active. This is a test notification confirming transactional email configuration.",
            recipients=recipients,
        )
        if not success:
            raise HTTPException(500, "Failed to dispatch test email via Brevo. Check server logs.")
        return {"ok": True, "message": f"Test email sent successfully to {recipients}"}

    @app.post("/api/integrations/instagram/detect")
    def detect_instagram():
        import httpx
        s = store.settings()
        keys = s.get("social_keys", {})
        token = keys.get("instagram_access_token") or keys.get("facebook_page_token", "")
        page_id = keys.get("facebook_page_id", "")
        account_id = keys.get("instagram_account_id", "")

        if not token:
            raise HTTPException(400, "Save a Facebook Page Access Token or Instagram Access Token in settings first.")

        # Option 1: Discover linked Instagram Business Account from Facebook Page
        if page_id:
            try:
                resp = httpx.get(
                    f"https://graph.facebook.com/v21.0/{page_id}?fields=name,instagram_business_account{{id,username,name,profile_picture_url}}&access_token={token}",
                    timeout=20
                )
                if resp.status_code == 200:
                    data = resp.json()
                    ig = data.get("instagram_business_account")
                    if ig:
                        discovered_id = ig.get("id")
                        if discovered_id and discovered_id != keys.get("instagram_account_id"):
                            keys["instagram_account_id"] = discovered_id
                            s["social_keys"] = keys
                            store.set_settings(s)
                        return {
                            "ok": True,
                            "connected": True,
                            "page_name": data.get("name"),
                            "account_id": discovered_id,
                            "username": ig.get("username"),
                            "name": ig.get("name"),
                            "profile_picture_url": ig.get("profile_picture_url"),
                            "source": "linked_via_facebook_page"
                        }
                elif resp.status_code >= 400:
                    err = resp.json().get("error", {}).get("message", resp.text)
                    if not account_id:
                        return {"ok": False, "connected": False, "error": err}
            except Exception as e:
                if not account_id:
                    return {"ok": False, "connected": False, "error": str(e)}

        # Option 2: Query direct Instagram Business Account ID
        if account_id:
            try:
                resp = httpx.get(
                    f"https://graph.facebook.com/v21.0/{account_id}?fields=id,username,name,profile_picture_url&access_token={token}",
                    timeout=20
                )
                if resp.status_code == 200:
                    ig = resp.json()
                    return {
                        "ok": True,
                        "connected": True,
                        "account_id": ig.get("id"),
                        "username": ig.get("username"),
                        "name": ig.get("name"),
                        "profile_picture_url": ig.get("profile_picture_url"),
                        "source": "direct_account_id"
                    }
                else:
                    return {"ok": False, "connected": False, "error": resp.json().get("error", {}).get("message", resp.text)}
            except Exception as e:
                return {"ok": False, "connected": False, "error": str(e)}

        return {
            "ok": False,
            "connected": False,
            "message": "No linked Instagram Business Account found. Ensure your Instagram Professional account is connected to your Facebook Page, or enter your Instagram Business Account ID directly."
        }

    @app.post("/api/integrations/whatsapp/test")
    def test_whatsapp_connection():
        import re, httpx
        keys = store.settings().get("social_keys", {})
        phone_number_id = keys.get("whatsapp_phone_number_id", "")
        token = keys.get("whatsapp_token", "") or keys.get("facebook_page_token", "")
        recipient = keys.get("whatsapp_recipient", "")

        if not phone_number_id:
            return {"ok": False, "connected": False, "error": "Enter a WhatsApp Phone Number ID in Social Integrations."}
        if not token:
            return {"ok": False, "connected": False, "error": "Enter a WhatsApp Cloud API Access Token (or ensure Facebook Page Token is saved)."}
        if not recipient:
            return {"ok": False, "connected": False, "error": "Enter a WhatsApp Recipient Phone Number to receive the test message."}

        clean_recipient = re.sub(r"[^\d]", "", recipient)
        if not clean_recipient:
            return {"ok": False, "connected": False, "error": "Recipient phone number must contain valid digits (including country code)."}

        phone_info = {}
        try:
            info_resp = httpx.get(
                f"https://graph.facebook.com/v21.0/{phone_number_id}?fields=id,display_phone_number,verified_name,quality_rating&access_token={token}",
                timeout=15
            )
            if info_resp.status_code == 200:
                phone_info = info_resp.json()
        except Exception:
            pass

        test_payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_recipient,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "🚀 Hello from Vtabsquare Marketing OS! Your WhatsApp Cloud API integration is connected and ready to broadcast."
            }
        }
        try:
            resp = httpx.post(
                f"https://graph.facebook.com/v21.0/{phone_number_id}/messages",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=test_payload,
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                msg_id = data.get("messages", [{}])[0].get("id", "")
                return {
                    "ok": True,
                    "connected": True,
                    "message_id": msg_id,
                    "display_phone_number": phone_info.get("display_phone_number", phone_number_id),
                    "verified_name": phone_info.get("verified_name", "WhatsApp Business"),
                    "recipient": clean_recipient
                }
            else:
                err_data = resp.json().get("error", {})
                err_msg = err_data.get("message", resp.text)
                return {"ok": False, "connected": False, "error": err_msg}
        except Exception as e:
            return {"ok": False, "connected": False, "error": str(e)}

    @app.get('/api/engagement')
    def engagement(): return community.list()

    @app.post('/api/engagement/sync')
    def sync_comments():
        count = community.sync_social_comments()
        return {'ok': True, 'queued': count, 'items': community.list()}

    @app.post('/api/engagement/{event_id}/decision')
    def decide_reply(event_id: str, data: ReplyDecision):
        return perform(lambda:community.decide(event_id,data.model_dump()))

    @app.post('/api/webhooks/engagement',status_code=202)
    async def receive_comment(request: Request):
        secret=os.environ.get('MARKETING_WEBHOOK_SECRET','')
        if len(secret)<32: raise HTTPException(503,'Configure the webhook signing secret on the server.')
        stamp=request.headers.get('x-marketing-timestamp','')
        try:
            if abs(time.time()-int(stamp))>300: raise ValueError()
        except ValueError: raise HTTPException(401,'Expired or invalid webhook timestamp.') from None
        chunks=[]; size=0
        async for chunk in request.stream():
            size+=len(chunk)
            if size>16000: raise HTTPException(413,'Webhook payload is too large.')
            chunks.append(chunk)
        body=b''.join(chunks)
        expected=hmac.new(secret.encode(),stamp.encode()+b'.'+body,hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected,request.headers.get('x-marketing-signature','')):
            raise HTTPException(401,'Invalid webhook signature.')
        try: data=Comment.model_validate_json(body)
        except ValueError: raise HTTPException(422,'Check the comment payload fields.') from None
        item=perform(lambda:community.receive(data.model_dump()))
        return {'id':item['id'],'state':item['state']}

    @app.get("/api/agents")
    def agents():
        return registry.snapshot(store.settings())

    @app.get("/api/campaigns")
    def campaigns():
        return store.list()

    @app.post("/api/campaigns", status_code=201)
    def create_campaign(brief: Brief):
        return perform(lambda: controller.create(brief.model_dump()))

    @app.get("/api/campaigns/{campaign_id}")
    def campaign(campaign_id: str):
        return perform(lambda: store.get(campaign_id))

    @app.post("/api/campaigns/{campaign_id}/approve")
    def approve(campaign_id: str, data: Decision):
        return perform(lambda: controller.approve(campaign_id, data.model_dump()))

    @app.post("/api/campaigns/{campaign_id}/revise")
    def revise(campaign_id: str, data: Revision):
        return perform(lambda: controller.revise(campaign_id, data.model_dump()))

    @app.post("/api/campaigns/{campaign_id}/cancel")
    def cancel(campaign_id: str):
        return perform(lambda: controller.cancel(campaign_id))

    @app.post("/api/campaigns/{campaign_id}/retry")
    def retry(campaign_id: str):
        return perform(lambda: controller.retry(campaign_id))

    @app.post('/api/campaigns/{campaign_id}/input')
    def answer_input(campaign_id: str, data: InputAnswer):
        return perform(lambda: controller.answer(campaign_id, data.model_dump()))

    @app.post("/api/campaigns/{campaign_id}/collect-metrics")
    def collect_campaign_metrics(campaign_id: str):
        from .integrations import collect_metrics
        c = perform(lambda: store.get(campaign_id))
        fresh_metrics = collect_metrics(c, store.settings())
        c.setdefault('results', {}).setdefault('analytics', {})['metrics'] = fresh_metrics
        if c.get('nodes', {}).get('analytics', {}).get('state') == 'SCHEDULED_WAIT':
            c['nodes']['analytics']['state'] = 'PENDING'
            c['nodes']['analytics']['not_before'] = 0
            with store.transaction() as db:
                Store.write(db, c)
            controller.step()
        else:
            with store.transaction() as db:
                Store.write(db, c)
        return store.get(campaign_id)

    @app.get("/api/campaigns/{campaign_id}/creative.svg")
    def creative(campaign_id: str):
        c = perform(lambda: store.get(campaign_id))
        if "creative" not in c["results"]:
            raise HTTPException(404, "Creative is not available yet.")
        from app.tools import brand_card
        return Response(content=brand_card(c), media_type="image/svg+xml")

    @app.get("/api/campaigns/{campaign_id}/export")
    def export(campaign_id: str):
        c = perform(lambda: store.get(campaign_id))
        return Response(json.dumps(c, indent=2), media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="campaign-{campaign_id}.json"'})

    dist = ROOT / "frontend" / "dist"
    if (dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/")
    def index():
        if not (dist / "index.html").exists():
            raise HTTPException(503, "Bundled dashboard is missing. Re-extract the complete project ZIP.")
        return FileResponse(dist / "index.html")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(status_code=204)

    return app
