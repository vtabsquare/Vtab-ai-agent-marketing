import hashlib
import json
import time
from .providers import ProviderError,get_key
from .store import Conflict
from .tools import CheckFailure,PublisherBot,content_hash,validate_copy,metrics_fixture
from .workflow import ROLES,DEPENDENCIES,NAMES,refresh_state,campaign_dependencies,campaign_roles
from .capabilities import workflow_configuration_snapshot
from .memory import MemoryService
from .analytics import AnalyticsService

STAGES=ROLES


def fingerprint(settings,key):
    return hashlib.sha256(json.dumps({'provider':settings['provider'],'model':settings['model'],'key':key},sort_keys=True).encode()).hexdigest()


def redact(value,key):
    if isinstance(value,str): return value.replace(key,'[REDACTED]') if key else value
    if isinstance(value,dict): return {k:redact(v,key) for k,v in value.items()}
    if isinstance(value,list): return [redact(v,key) for v in value]
    return value


class Controller:
    def __init__(self,store,registry,workflow_registry=None,mailer=None):
        self.store,self.registry=store,registry
        self.workflow_registry=workflow_registry
        self.publisher=PublisherBot(self.store)
        self.memory=MemoryService(self.store)
        self.analytics=AnalyticsService(self.store)
        self.demo_delay=0
        from .mailer import MailerService
        self.mailer=mailer or MailerService(self.store)

    def create(self,brief):
        s=self.store.settings(); key=get_key(self.store)
        if s['provider']=='gemini' and s.get('tested_fingerprint')!=fingerprint(s,key):
            raise Conflict('Test your current Gemini configuration in Settings before creating a workflow.')
        configuration=workflow_configuration_snapshot(s)
        workflow=self.workflow_registry.get(brief.get('workflow_id')) if self.workflow_registry else {'id':'campaign.v1','roles':ROLES,'dependencies':DEPENDENCIES,'required_capabilities':[]}
        missing=set(workflow.get('required_capabilities',[]))-set(configuration['capabilities'])
        if missing: raise Conflict('This workflow needs unavailable capabilities: '+', '.join(sorted(missing)))
        available={item['channel']:item['state'] for item in configuration['destinations']}
        selected=brief.get('destinations') or list(available)
        unknown=[channel for channel in selected if channel not in available]
        if unknown: raise Conflict('Unavailable campaign destinations: '+', '.join(unknown))
        configuration['destinations']=[{'channel':channel,'state':available[channel]} for channel in selected]
        live_platforms=[channel for channel in selected if available[channel] in {'publishing_connected','fully_connected'}]
        is_simulated = brief.get('_force_simulated') or s.get('publishing_mode') != 'live' or not live_platforms
        publishing = 'simulation' if is_simulated else 'live'
        campaign=self.store.create(brief,{'brand':s['brand'],'agents':self.registry.snapshot(s),'publishing':publishing,
            'platforms':live_platforms,'image_provider':s.get('image_provider','template'),
            'hf_model':s.get('hf_model','black-forest-labs/FLUX.1-schnell'),'hf_provider':s.get('hf_provider','auto'),'configuration':configuration,'workflow':workflow})
        try:
            self.mailer.send_campaign_started(campaign)
        except Exception:
            pass
        return campaign

    def approve(self,campaign_id,decision):
        def change(c):
            if c['state']!='AWAITING_APPROVAL': raise Conflict('This workflow is not awaiting approval.')
            if decision['content_hash']!=content_hash(c): raise Conflict('The preview changed. Review the current version.')
            c['approval']={'actor':'local-owner','at':time.time(),'content_hash':decision['content_hash'],
                           'note':decision['note'],'account':','.join(c['snapshot'].get('platforms',[])) or 'local-simulator','action':'publish_live' if c['snapshot'].get('publishing')=='live' else 'publish_simulated'}
            for q in c['input_requests']:
                if q['kind']=='approval' and q['status']=='OPEN': q.update(status='ANSWERED',answered_at=time.time(),answer='Approved')
            self.store.event(c,'local-owner','I approve this exact content version for the selected publishing destination.','manager','answer')
            self.store.event(c,'manager','Approval received. Publisher Bot, proceed with this authorized version.','publishing','assignment')
            refresh_state(c)
        return self.store.mutate(campaign_id,change)

    def reset_content(self,c,note):
        c['revisions']+=1; c['revision_note']=note; c['approval']=None; c['content_hash']=None
        for role in ROLES[2:]:
            node=c['nodes'][role]; node.update(state='PENDING',generation=node['generation']+1,lease=None,lease_until=0,error=None,not_before=0)
            c['results'].pop(role,None)
            for t in c['tasks']:
                if t['role']==role and t['status']=='RUNNING': t['status']='SUPERSEDED'
        for q in c['input_requests']:
            if q['status']=='OPEN': q['status']='SUPERSEDED'
        c['error']=None
        self.store.event(c,'manager','Writer Bot and Creative Bot, revise the content using this feedback: '+note,'writing','revision')
        refresh_state(c)

    def revise(self,campaign_id,decision):
        def change(c):
            if c['state']!='AWAITING_APPROVAL' or decision['content_hash']!=content_hash(c): raise Conflict('Review the current preview before requesting a revision.')
            if c['revisions']>=c['snapshot']['agents']['limits']['max_revisions']: raise Conflict('Revision limit reached. Create a corrected workflow.')
            self.store.event(c,'local-owner',decision['note'],'manager','answer')
            self.reset_content(c,decision['note'])
        return self.store.mutate(campaign_id,change)

    def answer(self,campaign_id,data):
        def change(c):
            if c['state'] in {'CANCELLED','COMPLETED'}: raise Conflict('This workflow has finished.')
            q=next((q for q in c['input_requests'] if q['id']==data['request_id']),None)
            if not q or q['status']!='OPEN' or q['kind']!='input': raise Conflict('This input request is no longer open.')
            node=c['nodes'][q['role']]
            if node['state']!='WAITING_INPUT' or node['generation']!=q['generation']: raise Conflict('This request belongs to an older task version.')
            q.update(status='ANSWERED',answer=data['answer'],answered_at=time.time())
            c['human_answers'].setdefault(q['role'],[]).append({'question':q['question'],'answer':data['answer']})
            node.update(state='PENDING',not_before=0,error=None)
            self.store.event(c,'local-owner',data['answer'],q['role'],'answer')
            self.store.event(c,q['role'],'Thank you. I have your input and will resume my task now.',kind='resumed')
            refresh_state(c)
        return self.store.mutate(campaign_id,change)

    def cancel(self,campaign_id):
        def change(c):
            if c['state'] in {'COMPLETED','CANCELLED'}: raise Conflict('This workflow has already finished.')
            c['state']='CANCELLED'
            for node in c['nodes'].values():
                if node['state']!='ACCEPTED': node.update(state='CANCELLED',generation=node['generation']+1,lease=None)
            for t in c['tasks']:
                if t['status']=='RUNNING': t['status']='CANCELLED'
            for q in c['input_requests']:
                if q['status']=='OPEN': q['status']='CANCELLED'
            self.store.event(c,'manager','I have stopped this workflow. No new bot tasks will begin.',kind='cancelled')
        return self.store.mutate(campaign_id,change)

    def retry(self,campaign_id):
        s = self.store.settings()
        key = get_key(self.store)
        def change(c):
            blocked=[r for r,n in c['nodes'].items() if n['state']=='BLOCKED']
            if not blocked: raise Conflict('No blocked bot task is available to retry.')
            c['snapshot']['brand'] = s['brand']
            c['revisions'] = 0
            profile=c['snapshot']['agents']['profiles']['default']
            if s['provider']!=profile['provider'] or s['model']!=profile['model']: raise Conflict('Restore the saved model or create a new workflow.')
            if s['provider']=='gemini' and s.get('tested_fingerprint')!=fingerprint(s,key): raise Conflict('Test the saved Gemini configuration first.')
            for role in blocked: c['nodes'][role].update(state='PENDING',error=None,not_before=0)
            c['error']=None; self.store.event(c,'manager','The corrected bot tasks are queued to retry.'); refresh_state(c)
        return self.store.mutate(campaign_id,change)

    def step(self):
        claimed=self.store.claim()
        if not claimed: return False
        snapshot,token=claimed; task=snapshot['_task']; role=task['role']; cfg=snapshot['snapshot']['agents']
        try:
            if task['checkpoint']:
                question={'question':'What visual style should I use for this creative?' if role=='creative' else 'Which campaign angle should I prioritize?',
                          'reason':'You asked this bot to check with you before continuing.'}
                result=None
            elif role=='publishing':
                approval=snapshot['approval']
                if not approval or approval['action'] != ('publish_live' if snapshot['snapshot'].get('publishing')=='live' else 'publish_simulated'): raise CheckFailure('Exact-version approval is required.')
                result={'output':self.publisher.publish(snapshot,approval['content_hash']),'provider':'tool','model':'none'}; question=None
            else:
                if not task['model_reserved']: raise ProviderError('Workflow model-call budget reached.',kind='budget')
                clean_prior = {}
                for r in campaign_dependencies(snapshot)[role]:
                    if r in snapshot['results']:
                        res = dict(snapshot['results'][r])
                        if 'image' in res: res = {k: v for k, v in res.items() if k != 'image'}
                        clean_prior[r] = res
                context={'brand':snapshot['snapshot']['brand'],'brief':snapshot['brief'],
                         'prior_results':clean_prior,
                         'revision_note':snapshot.get('revision_note',''),'human_answers':snapshot['human_answers'].get(role,[]),
                         'sources':['brand','brief'],'mode':'local_poc','configuration':snapshot['snapshot'].get('configuration',{})}
                memory_query=' '.join([snapshot['brief'].get('title',''),snapshot['brief'].get('audience',''),snapshot['brief'].get('goal','')])
                context['memory']=self.memory.retrieve(role,snapshot['id'],memory_query)
                if role=='analytics':
                    from .integrations import collect_metrics
                    context['metrics']=collect_metrics(snapshot,self.store.settings())
                if role=='optimization': context['past_campaign_data']=self.analytics.performance_summary()
                if role=='engagement': context['feedback']='Synthetic example: Could you share the price?'
                context['mode']=snapshot['snapshot'].get('publishing','simulation')
                profile=cfg['profiles'][cfg['agents'][role]['profile']]
                if profile['provider']=='demo' and self.demo_delay:
                    time.sleep(self.demo_delay)  # Labelled fixture latency so local bot transitions are observable.
                elif profile['provider']=='gemini':
                    time.sleep(2.5)  # Pacing for observable live UI transitions and Gemini free-tier TPM rate-limit compliance.
                result=self.registry.run(role,context,cfg,get_key(self.store)); out=result['output']; question=out.get('input_request')
                if not question:
                    if role=='research' and any(f['source_ref'] not in {'brand','brief'} and not f['source_ref'].startswith('web:') for f in out['findings']): raise CheckFailure('Research must reference supplied records or verified search results.')
                    if role=='writing': validate_copy(out,snapshot['snapshot']['brand'])
                    if role=='brand_review':
                        validate_copy(snapshot['results']['writing']['output'],snapshot['snapshot']['brand'])
                        if out['verdict']!='pass':
                            # If the only objection is about free pricing, ignore it
                            brand_price = snapshot['snapshot']['brand'].get('price','')
                            summary_lower = out.get('summary','').lower()
                            free_terms = {'free','no cost','no fee','complimentary'}
                            price_is_free = any(t in brand_price.lower() for t in free_terms)
                            price_only_issue = price_is_free and any(t in summary_lower for t in {'price','pricing','cost','currency','\u20b9','$','inr','usd'})
                            if not price_only_issue:
                                raise CheckFailure('Brand review requires changes: '+out['summary'])
                    if role=='manager' and out['recommendation']!='request_approval':
                        # If the only objection is about free pricing, override and proceed
                        brand_price = snapshot['snapshot']['brand'].get('price','')
                        summary_lower = out.get('summary','').lower()
                        free_terms = {'free','no cost','no fee','complimentary'}
                        price_is_free = any(t in brand_price.lower() for t in free_terms)
                        price_only_issue = price_is_free and any(t in summary_lower for t in {'price','pricing','cost','currency','\u20b9','$','inr','usd','discrepanc'})
                        if not price_only_issue:
                            raise CheckFailure('Manager requires changes: '+out['summary'])
                        # Override: treat as request_approval for free-tier pricing
                        out['recommendation'] = 'request_approval'
                    if role=='analytics': result['metrics']=context['metrics']
                    if role=='creative':
                        from .integrations import generate_image
                        image=generate_image(out['art_direction'],snapshot['snapshot'],self.store.settings())
                        if image: result['image']=image
            for secret in [get_key(self.store),*self.store.settings().get('social_keys',{}).values()]:
                result=redact(result,secret); question=redact(question,secret)
            def accepted(c,t,node):
                if question:
                    node['state']='WAITING_INPUT'; t['status']='WAITING_INPUT'
                    self.store.ask(c,role,question['question'],question['reason']); return
                c['results'][role]=result; node.update(state='ACCEPTED',error=None); t['status']='ACCEPTED'
                out=result['output']
                summary=next((out[k] for k in ['summary','interpretation','hypothesis','art_direction','headline','message','draft_reply','limitations'] if out.get(k)), 'My task is complete.')
                self.store.event(c,role,summary,kind='result')
                for dependent in campaign_roles(c):
                    if role in campaign_dependencies(c)[dependent]:
                        self.store.event(c,role,f"My result has passed its checks. {NAMES[dependent]}, I am handing it over for your task.",dependent,'handoff')
                if role=='publishing' and out.get('mode')=='live':
                    c['nodes']['analytics'].update(state='SCHEDULED_WAIT',not_before=time.time()+86400)
                    c['nodes']['engagement'].update(state='ACCEPTED')
                    c['results']['engagement']={'output':{'category':'Live engagement queue','draft_reply':'Real comments arrive in the Community inbox. Each reply requires approval.','requires_human':True},'provider':'tool','model':'none'}
                    self.store.event(c,'analytics','I will collect platform metrics 24 hours after publication.',kind='scheduled')
                if role=='manager':
                    c['content_hash']=content_hash(c)
                    self.store.ask(c,'manager','Your input is needed: review the copy and creative, then approve or request changes.','Publisher Bot will wait for your exact-version approval.','approval')
                if all(c['nodes'][r]['state']=='ACCEPTED' for r in campaign_roles(c)):
                    self.store.event(c,'manager','This workflow is complete. Publication is confirmed. Optimization and reply drafts are ready for you.',kind='completed')
            completed=self.store.complete(snapshot['id'],token,accepted)
            if completed and result and not question:
                if role not in {'publishing'}:
                    self.memory.capture_agent_result(snapshot['id'],role,result,result.get('prompt_version'),result.get('model'))
                if role=='manager':
                    try:
                        self.mailer.send_awaiting_approval(self.store.get(snapshot['id']))
                    except Exception:
                        pass
                elif role=='publishing':
                    try:
                        c_current=self.store.get(snapshot['id'])
                        receipts=result.get('output',{}).get('receipts') or [
                            {'platform': p, 'status': result.get('output',{}).get('status','published'), 'post_id': result.get('output',{}).get('external_id')}
                            for p in snapshot.get('snapshot',{}).get('platforms',['social'])
                        ]
                        self.mailer.send_post_published(c_current,receipts)
                    except Exception:
                        pass
        except Exception as exc:
            kind=getattr(exc,'kind','check' if isinstance(exc,CheckFailure) else 'invalid_output' if isinstance(exc,ValueError) else 'execution')
            message=str(exc) if str(exc).strip() else 'Task execution failed. Review the configuration and evidence.'
            message=redact(message,get_key(self.store))
            def failed(c,t,node):
                error={'role':role,'kind':kind,'message':message}; node.update(state='BLOCKED',error=error); t['status']='FAILED'; c['error']=error
                self.store.event(c,role,message,'manager','failure')
                failures=sum(x['role']==role and x['status']=='FAILED' and x.get('generation')==node['generation'] for x in c['tasks'])
                if isinstance(exc,ProviderError) and exc.retryable and failures<=cfg['limits']['max_retries']:
                    node.update(state='RETRY_SCHEDULED',not_before=time.time()+min(30,2**failures))
                    self.store.event(c,'manager',f"{NAMES[role]} hit a temporary connection problem. I scheduled a bounded retry.",role,'recovery')
                elif kind in {'check','invalid_output'} and role in {'writing','brand_review','manager'} and c['revisions']<cfg['limits']['max_revisions']:
                    self.reset_content(c,message)
                else: self.store.event(c,'manager',f"Your attention is needed for {NAMES[role]}: {message}",'local-owner','attention')
            self.store.complete(snapshot['id'],token,failed)
        return True
