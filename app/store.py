import json
import sqlite3
import time
import uuid
import queue
import re
import threading
from contextlib import contextmanager
from pathlib import Path
from .workflow import ROLES, NAMES, DEPENDENCIES, START_MESSAGES, nodes, ready, refresh_state, campaign_roles
from .capabilities import normalize_settings


class Conflict(ValueError): pass
class Missing(ValueError): pass

DEFAULT_SETTINGS = {'provider': 'demo', 'model': 'deterministic-demo-v1', 'tested_fingerprint': '',
 'brand': {'name':'Northstar Studio','product':'Brand launch package','price':'INR 2,499',
           'tone':'Clear, friendly and practical','facts':'Includes a brand consultation and three social post designs.'}}


class Store:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True,exist_ok=True)
        self.path = self.folder/'marketing.db'
        self.pool = queue.LifoQueue(maxsize=8)
        self.pool_slots = threading.BoundedSemaphore(8)
        from .credentials import Vault
        self.vault = Vault(self.folder)
        with self.transaction() as db:
            db.executescript('''PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY,applied_at REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS settings(id INTEGER PRIMARY KEY,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS campaigns(id TEXT PRIMARY KEY,payload TEXT NOT NULL,lease TEXT,lease_until REAL NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS publications(id TEXT PRIMARY KEY,status TEXT NOT NULL,payload TEXT);
            CREATE TABLE IF NOT EXISTS engagement(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS website_scans(id TEXT PRIMARY KEY,root_url TEXT NOT NULL,created_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS knowledge_items(id TEXT PRIMARY KEY,kind TEXT NOT NULL,item_key TEXT NOT NULL,status TEXT NOT NULL,created_at REAL NOT NULL,updated_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS catalog_items(id TEXT PRIMARY KEY,created_at REAL NOT NULL,updated_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS audiences(id TEXT PRIMARY KEY,created_at REAL NOT NULL,updated_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS leads(id TEXT PRIMARY KEY,dedupe_key TEXT,created_at REAL NOT NULL,updated_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE UNIQUE INDEX IF NOT EXISTS leads_dedupe_key ON leads(dedupe_key) WHERE dedupe_key IS NOT NULL;
            CREATE TABLE IF NOT EXISTS memories(id TEXT PRIMARY KEY,scope TEXT NOT NULL,memory_type TEXT NOT NULL,status TEXT NOT NULL,sensitivity TEXT NOT NULL,expires_at REAL,created_at REAL NOT NULL,updated_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS memories_scope_status ON memories(scope,status,updated_at);
            CREATE TABLE IF NOT EXISTS landing_pages(id TEXT PRIMARY KEY,slug TEXT UNIQUE NOT NULL,form_token TEXT UNIQUE NOT NULL,status TEXT NOT NULL,updated_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS metric_events(id TEXT PRIMARY KEY,event_type TEXT NOT NULL,source TEXT NOT NULL,campaign_id TEXT,occurred_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS metric_events_campaign ON metric_events(campaign_id,event_type,occurred_at);
            CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY,campaign_id TEXT,status TEXT NOT NULL,created_at REAL NOT NULL,updated_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS connector_records(id TEXT PRIMARY KEY,connector_id TEXT NOT NULL,entity_type TEXT NOT NULL,external_id TEXT NOT NULL,synced_at REAL NOT NULL,payload TEXT NOT NULL,UNIQUE(connector_id,entity_type,external_id));
            CREATE TABLE IF NOT EXISTS connector_states(connector_id TEXT PRIMARY KEY,updated_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS connector_dead_letters(id TEXT PRIMARY KEY,connector_id TEXT NOT NULL,created_at REAL NOT NULL,kind TEXT NOT NULL,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS connector_outbox(id TEXT PRIMARY KEY,connector_id TEXT NOT NULL,status TEXT NOT NULL,created_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,email TEXT UNIQUE NOT NULL,role TEXT NOT NULL,active INTEGER NOT NULL,password_hash TEXT NOT NULL,created_at REAL NOT NULL,updated_at REAL NOT NULL,payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY,user_id TEXT NOT NULL,token_hash TEXT UNIQUE NOT NULL,created_at REAL NOT NULL,expires_at REAL NOT NULL);
            CREATE INDEX IF NOT EXISTS sessions_token_expiry ON sessions(token_hash,expires_at);
            CREATE TABLE IF NOT EXISTS audit_events(id TEXT PRIMARY KEY,occurred_at REAL NOT NULL,actor_id TEXT NOT NULL,path TEXT NOT NULL,status INTEGER NOT NULL,payload TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS audit_events_time ON audit_events(occurred_at);
            CREATE TABLE IF NOT EXISTS secrets(id INTEGER PRIMARY KEY,api_key TEXT NOT NULL);''')
            db.execute('INSERT OR IGNORE INTO schema_migrations VALUES(1,?)',(time.time(),))
            db.execute('INSERT OR IGNORE INTO schema_migrations VALUES(2,?)',(time.time(),))
            db.execute('INSERT OR IGNORE INTO schema_migrations VALUES(3,?)',(time.time(),))
            db.execute('INSERT OR IGNORE INTO schema_migrations VALUES(4,?)',(time.time(),))
            db.execute('INSERT OR IGNORE INTO schema_migrations VALUES(5,?)',(time.time(),))
            db.execute('INSERT OR IGNORE INTO schema_migrations VALUES(6,?)',(time.time(),))
            db.execute('INSERT OR IGNORE INTO schema_migrations VALUES(7,?)',(time.time(),))
            db.execute('INSERT OR IGNORE INTO schema_migrations VALUES(8,?)',(time.time(),))
            db.execute('INSERT OR IGNORE INTO settings VALUES(1,?)',(json.dumps(DEFAULT_SETTINGS),))
            for row in db.execute('SELECT * FROM campaigns').fetchall():
                c = json.loads(row['payload'])
                if 'nodes' not in c:
                    self.migrate(c)
                    db.execute('UPDATE campaigns SET payload=?,lease=NULL,lease_until=0 WHERE id=?',(json.dumps(c),c['id']))

        self.set_settings(self.settings(), self.key())

    def connect(self):
        db=sqlite3.connect(self.path,timeout=30,check_same_thread=False)
        db.execute("PRAGMA busy_timeout=30000")
        db.row_factory=sqlite3.Row
        return db

    @contextmanager
    def pooled(self):
        if not self.pool_slots.acquire(timeout=30):
            raise Conflict('The database is busy. Please retry in a moment.')
        db=None
        try:
            try: db=self.pool.get_nowait()
            except queue.Empty: db=self.connect()
            yield db
        finally:
            if db is not None:
                if db.in_transaction: db.rollback()
                self.pool.put_nowait(db)
            self.pool_slots.release()

    def close(self):
        while True:
            try: self.pool.get_nowait().close()
            except queue.Empty: return

    @contextmanager
    def transaction(self):
        with self.pooled() as db:
            try:
                db.execute('BEGIN IMMEDIATE')
                yield db
                db.commit()
            except Exception:
                db.rollback()
                raise

    @contextmanager
    def reading(self):
        with self.pooled() as db: yield db

    def settings(self):
        with self.reading() as db:
            settings=normalize_settings(json.loads(db.execute('SELECT payload FROM settings WHERE id=1').fetchone()[0]))
            settings['social_keys']={k:self.vault.decode(v) for k,v in settings.get('social_keys',{}).items()}
            return settings

    def key(self):
        with self.reading() as db:
            row=db.execute('SELECT api_key FROM secrets WHERE id=1').fetchone()
            return self.vault.decode(row[0]) if row else ''

    def set_settings(self,settings,key=None):
        settings=normalize_settings(json.loads(json.dumps(settings)))
        settings['social_keys']={k:self.vault.encode(v) for k,v in settings.get('social_keys',{}).items()}
        with self.transaction() as db:
            db.execute('UPDATE settings SET payload=? WHERE id=1',(json.dumps(settings),))
            if key is not None: db.execute('INSERT OR REPLACE INTO secrets VALUES(1,?)',(self.vault.encode(key),))

    @staticmethod
    def event(c,actor,message,target=None,kind='message'):
        c['events'].append({'id':uuid.uuid4().hex,'at':time.time(),'actor':actor,'message':message,
                            'target':target,'kind':kind})

    @staticmethod
    def write(db,c):
        c['version']+=1
        c['updated_at']=time.time()
        db.execute('UPDATE campaigns SET payload=? WHERE id=?',(json.dumps(c),c['id']))

    @staticmethod
    def ask(c,role,question,reason,kind='input'):
        request={'id':uuid.uuid4().hex,'role':role,'question':question,'reason':reason,
                 'kind':kind,'status':'OPEN','created_at':time.time(),'generation':c['nodes'][role]['generation']}
        c['input_requests'].append(request)
        Store.event(c,role,question,'local-owner','input_needed')
        return request

    @staticmethod
    def migrate(c):
        c['nodes']=nodes()
        c['input_requests']=[]
        c['human_answers']={}
        for role in ROLES:
            if role in c['results']: c['nodes'][role]['state']='ACCEPTED'
        for t in c['tasks']:
            role=t.get('role') or ROLES[t['stage']]
            t['role']=role
            c['nodes'][role]['attempt']=max(c['nodes'][role]['attempt'],t['attempt'])
            if t['status']=='RUNNING': t['status']='INTERRUPTED'
        if c['state']=='BLOCKED' and c.get('error'):
            c['nodes'][c['error']['role']]['state']='BLOCKED'
            c['nodes'][c['error']['role']]['error']=c['error']
        if c['state']=='AWAITING_APPROVAL':
            Store.ask(c,'manager','Your input is needed: review and approve this content version.','Publishing waits for your authorization.','approval')
        refresh_state(c)
        Store.event(c,'manager','Your saved campaign is now available as an independent workflow.')

    def create(self,brief,snapshot):
        now=time.time()
        c={'id':uuid.uuid4().hex,'version':1,'brief':brief,'snapshot':snapshot,'state':'QUEUED',
           'stage':0,'created_at':now,'updated_at':now,'results':{},'tasks':[],'events':[],
           'approval':None,'error':None,'not_before':0,'revisions':0,'model_calls':0,
           'content_hash':None,'operation_id':uuid.uuid4().hex,'nodes':nodes(),'input_requests':[],'human_answers':{}}
        self.event(c,'manager',f"I've opened {brief['title']}. Research Bot, check the supplied brief and brand facts first.",'research','assignment')
        self.event(c,'manager','Each bot has its own task. I will coordinate handoffs and ask you when a decision is needed.')
        with self.transaction() as db: db.execute('INSERT INTO campaigns(id,payload) VALUES(?,?)',(c['id'],json.dumps(c)))
        return c

    def get(self,campaign_id):
        with self.reading() as db:
            row=db.execute('SELECT payload FROM campaigns WHERE id=?',(campaign_id,)).fetchone()
            if not row: raise Missing('Workflow not found.')
            return json.loads(row[0])

    def list(self):
        with self.reading() as db: rows=db.execute('SELECT payload FROM campaigns').fetchall()
        return sorted((json.loads(r[0]) for r in rows),key=lambda c:c['created_at'],reverse=True)

    def save_website_scan(self,root_url,pages,items):
        now=time.time(); scan_id=uuid.uuid4().hex
        with self.transaction() as db:
            previous={row['item_key']:json.loads(row['payload']) for row in db.execute("SELECT item_key,payload FROM knowledge_items WHERE kind IN ('website_summary','price_candidate') AND status!='rejected'").fetchall()}
            created=[]; changed=[]
            for item in items:
                prior=previous.get(item['key'])
                if prior and prior.get('content_hash')==item.get('content_hash'): continue
                item_id=uuid.uuid4().hex; payload={**item,'id':item_id,'created_at':now,'updated_at':now,'decision_note':''}
                db.execute('INSERT INTO knowledge_items VALUES(?,?,?,?,?,?,?)',(item_id,item['kind'],item['key'],item['status'],now,now,json.dumps(payload)))
                created.append(payload)
                if prior: changed.append({'key':item['key'],'previous_id':prior['id'],'current_id':item_id})
            scan={'id':scan_id,'root_url':root_url,'created_at':now,'pages':pages,'new_items':len(created),'changed_items':changed}
            db.execute('INSERT INTO website_scans VALUES(?,?,?,?)',(scan_id,root_url,now,json.dumps(scan)))
        return scan

    def knowledge(self,status=None):
        with self.reading() as db:
            if status: rows=db.execute('SELECT payload FROM knowledge_items WHERE status=? ORDER BY updated_at DESC',(status,)).fetchall()
            else: rows=db.execute('SELECT payload FROM knowledge_items ORDER BY updated_at DESC').fetchall()
        return [json.loads(row[0]) for row in rows]

    def decide_knowledge(self,item_id,status,note=''):
        with self.transaction() as db:
            row=db.execute('SELECT payload FROM knowledge_items WHERE id=?',(item_id,)).fetchone()
            if not row: raise Missing('Knowledge item not found.')
            item=json.loads(row[0]); item.update(status=status,decision_note=note,updated_at=time.time())
            db.execute('UPDATE knowledge_items SET status=?,updated_at=?,payload=? WHERE id=?',(status,item['updated_at'],json.dumps(item),item_id))
        return item

    def create_record(self,table,payload):
        if table not in {'catalog_items','audiences'}: raise ValueError('Unsupported record table.')
        now=time.time(); item={**payload,'id':uuid.uuid4().hex,'created_at':now,'updated_at':now}
        with self.transaction() as db: db.execute(f'INSERT INTO {table} VALUES(?,?,?,?)',(item['id'],now,now,json.dumps(item)))
        return item

    def list_records(self,table):
        if table not in {'catalog_items','audiences'}: raise ValueError('Unsupported record table.')
        with self.reading() as db: rows=db.execute(f'SELECT payload FROM {table} ORDER BY updated_at DESC').fetchall()
        return [json.loads(row[0]) for row in rows]

    @staticmethod
    def _lead_key(payload):
        email=payload.get('email','').strip().lower(); phone=re.sub(r'\D','',payload.get('phone',''))
        return 'email:'+email if email else ('phone:'+phone if phone else None)

    def create_lead(self,payload):
        if not payload.get('email') and not payload.get('phone') and not payload.get('name'):
            raise Conflict('Enter at least a name, email, or phone number.')
        now=time.time(); key=self._lead_key(payload)
        item={**payload,'id':uuid.uuid4().hex,'status':'new','owner':'','follow_up_at':None,'notes':[],
              'created_at':now,'updated_at':now}
        try:
            with self.transaction() as db: db.execute('INSERT INTO leads VALUES(?,?,?,?,?)',(item['id'],key,now,now,json.dumps(item)))
        except sqlite3.IntegrityError: raise Conflict('A lead with this email or phone already exists.') from None
        return item

    def leads(self):
        with self.reading() as db: rows=db.execute('SELECT payload FROM leads ORDER BY updated_at DESC').fetchall()
        return [json.loads(row[0]) for row in rows]

    def update_lead(self,lead_id,changes):
        with self.transaction() as db:
            row=db.execute('SELECT payload FROM leads WHERE id=?',(lead_id,)).fetchone()
            if not row: raise Missing('Lead not found.')
            item=json.loads(row[0]); note=changes.pop('note',None)
            for key,value in changes.items():
                if value is not None: item[key]=value
            if note: item.setdefault('notes',[]).append({'text':note,'at':time.time()})
            item['updated_at']=time.time(); db.execute('UPDATE leads SET updated_at=?,payload=? WHERE id=?',(item['updated_at'],json.dumps(item),lead_id))
        return item

    def delete_lead(self,lead_id):
        with self.transaction() as db:
            if not db.execute('SELECT 1 FROM leads WHERE id=?',(lead_id,)).fetchone(): raise Missing('Lead not found.')
            db.execute('DELETE FROM leads WHERE id=?',(lead_id,))
        return {'deleted':True,'id':lead_id}

    def mutate(self,campaign_id,fn):
        with self.transaction() as db:
            row=db.execute('SELECT payload FROM campaigns WHERE id=?',(campaign_id,)).fetchone()
            if not row: raise Missing('Workflow not found.')
            c=json.loads(row[0]); fn(c); self.write(db,c); return c

    def claim(self):
        with self.transaction() as db:
            all_c=[json.loads(r[0]) for r in db.execute('SELECT payload FROM campaigns').fetchall()]
            active=sum(n['state']=='RUNNING' and n['lease_until']>time.time() for c in all_c for n in c['nodes'].values())
            if active>=4: return None
            # Least recently updated workflow first: a busy workflow cannot monopolize the queue.
            for c in sorted(all_c,key=lambda item:item['updated_at']):
                if c['state'] in {'COMPLETED','CANCELLED'}: continue
                dirty=False
                for role,node in c['nodes'].items():
                    if node['state']=='RUNNING' and node['lease_until']<time.time():
                        node.update(state='PENDING',lease=None)
                        for t in c['tasks']:
                            if t['role']==role and t['status']=='RUNNING': t['status']='INTERRUPTED'
                        self.event(c,role,'I am resuming my interrupted task from its saved checkpoint.',kind='recovery'); dirty=True
                if sum(n['state']=='RUNNING' for n in c['nodes'].values())>=2: continue
                for role in campaign_roles(c):
                    node=c['nodes'][role]
                    if not ready(c,role) or node['not_before']>time.time(): continue
                    token=uuid.uuid4().hex
                    node.update(state='RUNNING',lease=token,lease_until=time.time()+120,attempt=node['attempt']+1)
                    checkpoint=c['brief'].get('checkpoint')==role and not c['human_answers'].get(role)
                    reserved=role!='publishing' and not checkpoint and c['model_calls']<c['snapshot']['agents']['limits']['max_model_calls']
                    if reserved: c['model_calls']+=1
                    task={'id':uuid.uuid4().hex,'token':token,'role':role,'stage':ROLES.index(role),'status':'RUNNING',
                          'attempt':node['attempt'],'generation':node['generation'],'started_at':time.time(),
                          'input_version':c['version'],'model_reserved':reserved,'checkpoint':checkpoint}
                    c['tasks'].append(task)
                    self.event(c,role,START_MESSAGES[role],kind='started')
                    refresh_state(c); self.write(db,c)
                    # Return the exact assigned task identity; other workers may claim sibling tasks next.
                    c['_task']=task
                    return c,token
                if dirty: refresh_state(c); self.write(db,c)
        return None

    def complete(self,campaign_id,token,fn):
        with self.transaction() as db:
            row=db.execute('SELECT payload FROM campaigns WHERE id=?',(campaign_id,)).fetchone()
            c=json.loads(row[0])
            task=next((t for t in c['tasks'] if t.get('token')==token),None)
            if not task or c['state']=='CANCELLED': return False
            node=c['nodes'][task['role']]
            if node['lease']!=token or node['generation']!=task['generation'] or task['status']!='RUNNING': return False
            fn(c,task,node)
            node.update(lease=None,lease_until=0)
            task['finished_at']=time.time()
            refresh_state(c); self.write(db,c)
            return True
