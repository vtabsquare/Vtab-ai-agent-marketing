"""Governed, inspectable memory. Agents receive scoped records, never hidden reasoning."""
import json
import time
import uuid
from .store import Missing, Conflict

ALLOWED_STATUSES={'candidate','approved','rejected','superseded','expired'}
ALLOWED_SENSITIVITY={'public','internal','confidential','personal'}

def readable_scopes(role,campaign_id=None):
    scopes={'client','performance','agent.'+role}
    if campaign_id: scopes.add('campaign.'+campaign_id)
    return scopes

class MemoryService:
    def __init__(self,store): self.store=store

    def create(self,data,created_by='user'):
        if data['status'] not in ALLOWED_STATUSES or data['sensitivity'] not in ALLOWED_SENSITIVITY:
            raise Conflict('Memory status or sensitivity is invalid.')
        now=time.time(); record={**data,'id':uuid.uuid4().hex,'created_at':now,'updated_at':now,
                                 'created_by':created_by,'supersedes_id':data.get('supersedes_id')}
        with self.store.transaction() as db:
            if record.get('supersedes_id'):
                prior=db.execute('SELECT payload FROM memories WHERE id=?',(record['supersedes_id'],)).fetchone()
                if not prior: raise Missing('Memory to supersede was not found.')
                old=json.loads(prior[0]); old.update(status='superseded',updated_at=now)
                db.execute('UPDATE memories SET status=?,updated_at=?,payload=? WHERE id=?',('superseded',now,json.dumps(old),old['id']))
            db.execute('INSERT INTO memories VALUES(?,?,?,?,?,?,?,?,?)',
                       (record['id'],record['scope'],record['memory_type'],record['status'],record['sensitivity'],
                        record.get('expires_at'),now,now,json.dumps(record)))
        return record

    def list(self,status=None,scope=None):
        clauses=[]; values=[]
        if status: clauses.append('status=?'); values.append(status)
        if scope: clauses.append('scope=?'); values.append(scope)
        where=(' WHERE '+' AND '.join(clauses)) if clauses else ''
        with self.store.reading() as db: rows=db.execute('SELECT payload FROM memories'+where+' ORDER BY updated_at DESC',values).fetchall()
        return [json.loads(row[0]) for row in rows]

    def decide(self,memory_id,status,note=''):
        if status not in {'approved','rejected','superseded'}: raise Conflict('Unsupported memory decision.')
        with self.store.transaction() as db:
            row=db.execute('SELECT payload FROM memories WHERE id=?',(memory_id,)).fetchone()
            if not row: raise Missing('Memory not found.')
            record=json.loads(row[0]); record.update(status=status,decision_note=note,updated_at=time.time())
            db.execute('UPDATE memories SET status=?,updated_at=?,payload=? WHERE id=?',(status,record['updated_at'],json.dumps(record),memory_id))
        return record

    def delete(self,memory_id):
        with self.store.transaction() as db:
            if not db.execute('SELECT 1 FROM memories WHERE id=?',(memory_id,)).fetchone(): raise Missing('Memory not found.')
            db.execute('DELETE FROM memories WHERE id=?',(memory_id,))
        return {'deleted':True,'id':memory_id}

    def retrieve(self,role,campaign_id,query='',limit=8):
        scopes=readable_scopes(role,campaign_id); now=time.time(); candidates=[]
        with self.store.reading() as db:
            for scope in scopes:
                rows=db.execute("SELECT payload FROM memories WHERE scope=? AND status='approved' AND (expires_at IS NULL OR expires_at>?) ORDER BY updated_at DESC LIMIT 50",(scope,now)).fetchall()
                candidates.extend(json.loads(row[0]) for row in rows)
        terms={term.casefold() for term in query.split() if len(term)>2}
        def score(item):
            text=(item.get('content','')+' '+' '.join(item.get('tags',[]))).casefold()
            return sum(term in text for term in terms),item['updated_at']
        return sorted(candidates,key=score,reverse=True)[:max(1,min(limit,20))]

    def capture_agent_result(self,campaign_id,role,result,prompt_version=None,model=None):
        content=json.dumps(result.get('output',{}),ensure_ascii=False,sort_keys=True)
        return self.create({'scope':'campaign.'+campaign_id,'memory_type':'agent_result','content':content[:12000],
                            'source':'campaign_result','source_id':campaign_id,'confidence':1.0,'status':'approved',
                            'sensitivity':'internal','tags':[role],'expires_at':None,'prompt_version':prompt_version,
                            'model_version':model,'supersedes_id':None},created_by='system')
