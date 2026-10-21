"""Canonical events, funnel reporting and controlled marketing experiments."""
import json
import math
import time
import uuid
from .store import Missing, Conflict

class AnalyticsService:
    def __init__(self,store): self.store=store
    def funnel(self,campaign_id=None):
        with self.store.reading() as db:
            if campaign_id: rows=db.execute('SELECT event_type,COUNT(*) n FROM metric_events WHERE campaign_id=? GROUP BY event_type',(campaign_id,)).fetchall()
            else: rows=db.execute('SELECT event_type,COUNT(*) n FROM metric_events GROUP BY event_type').fetchall()
        counts={row['event_type']:row['n'] for row in rows}
        views=counts.get('page_view',0); leads=counts.get('form_submit',0); conversions=counts.get('conversion',0)
        return {'campaign_id':campaign_id,'events':counts,'lead_conversion_pct':round(leads/views*100,2) if views else None,
                'customer_conversion_pct':round(conversions/leads*100,2) if leads else None,
                'limitations':'Rates use recorded events only; missing tracking sources remain unavailable.'}
    def performance_summary(self,limit=20):
        with self.store.reading() as db:
            if getattr(self.store, '_use_pg', False):
                try:
                    rows = db.execute("SELECT payload FROM campaigns ORDER BY (payload::json->>'updated_at')::float DESC LIMIT %s", (limit,)).fetchall()
                except Exception:
                    rows = db.execute("SELECT payload FROM campaigns").fetchall()
            else:
                try:
                    rows = db.execute("SELECT payload FROM campaigns ORDER BY json_extract(payload,'$.updated_at') DESC LIMIT ?", (limit,)).fetchall()
                except Exception:
                    rows = db.execute("SELECT payload FROM campaigns").fetchall()
        summary=[]
        for row in rows:
            campaign=json.loads(row[0]); analytics=campaign.get('results',{}).get('analytics',{})
            if analytics: summary.append({'campaign_id':campaign['id'],'title':campaign['brief']['title'],'metrics':analytics.get('metrics'),
                                          'interpretation':analytics.get('output',{}).get('interpretation')})
        return summary
    def create_experiment(self,data):
        if len(data['variants'])<2: raise Conflict('An experiment needs at least two variants.')
        now=time.time(); experiment={**data,'id':uuid.uuid4().hex,'status':'draft','results':{},'created_at':now,'updated_at':now}
        with self.store.transaction() as db: db.execute('INSERT INTO experiments VALUES(?,?,?,?,?,?)',(experiment['id'],data.get('campaign_id'),experiment['status'],now,now,json.dumps(experiment)))
        return experiment
    def experiments(self):
        with self.store.reading() as db: rows=db.execute('SELECT payload FROM experiments ORDER BY updated_at DESC').fetchall()
        return [json.loads(row[0]) for row in rows]
    def record(self,experiment_id,data):
        with self.store.transaction() as db:
            row=db.execute('SELECT payload FROM experiments WHERE id=?',(experiment_id,)).fetchone()
            if not row: raise Missing('Experiment not found.')
            experiment=json.loads(row[0]); variant=data['variant']
            if variant not in {item['id'] for item in experiment['variants']}: raise Conflict('Unknown experiment variant.')
            experiment['results'][variant]={'exposures':data['exposures'],'conversions':data['conversions'],
                'rate_pct':round(data['conversions']/data['exposures']*100,2) if data['exposures'] else None}
            experiment.update(status='running',updated_at=time.time())
            if len(experiment['results'])==len(experiment['variants']):
                ranked=sorted(experiment['results'].items(),key=lambda item:item[1]['rate_pct'] if item[1]['rate_pct'] is not None else -1,reverse=True)
                experiment['analysis']={'leader':ranked[0][0],'difference_pct_points':round(ranked[0][1]['rate_pct']-ranked[1][1]['rate_pct'],2),
                    'note':'Descriptive comparison only; validate sample size and statistical confidence before rollout.'}
            db.execute('UPDATE experiments SET status=?,updated_at=?,payload=? WHERE id=?',(experiment['status'],experiment['updated_at'],json.dumps(experiment),experiment_id))
        return experiment
    def close(self,experiment_id):
        with self.store.transaction() as db:
            row=db.execute('SELECT payload FROM experiments WHERE id=?',(experiment_id,)).fetchone()
            if not row: raise Missing('Experiment not found.')
            experiment=json.loads(row[0]); experiment.update(status='completed',updated_at=time.time())
            db.execute('UPDATE experiments SET status=?,updated_at=?,payload=? WHERE id=?',('completed',experiment['updated_at'],json.dumps(experiment),experiment_id))
        return experiment
