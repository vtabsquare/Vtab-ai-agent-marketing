"""Canonical connector SDK with idempotent inbound sync and controlled outbound queue."""
import json
import time
import uuid
from .store import Missing, Conflict

ENTITY_TYPES={'contact','account','product','segment','interaction','conversion','consent'}
CONNECTOR_TYPES={
 'crm':{'name':'CRM compatibility connector','capabilities':['crm.read','crm.write'],'description':'Compatibility alias for a normalized CRM connector.'},
 'generic_crm':{'name':'Generic CRM','capabilities':['crm.read','crm.write'],'description':'Synchronize canonical CRM records through an adapter or trusted bridge.'},
 'generic_webhook':{'name':'Generic webhook','capabilities':['webhook.read'],'description':'Receive normalized records from a trusted integration bridge.'},
 'hubspot':{'name':'HubSpot','capabilities':['crm.read','crm.write'],'description':'HubSpot adapter contract; account authorization is configured separately.'},
 'salesforce':{'name':'Salesforce','capabilities':['crm.read','crm.write'],'description':'Salesforce adapter contract; account authorization is configured separately.'}
}

class ConnectorService:
    def __init__(self,store): self.store=store
    def types(self): return [{'type':key,**value} for key,value in CONNECTOR_TYPES.items()]
    def configuration(self,connector_id):
        connector=next((item for item in self.store.settings().get('connectors',[]) if item.get('id')==connector_id),None)
        if not connector or not connector.get('enabled'): raise Missing('Enabled connector not found.')
        if connector.get('type') not in CONNECTOR_TYPES: raise Conflict('Connector type is not registered.')
        return connector
    def sync(self,connector_id,records,cursor=None):
        connector=self.configuration(connector_id); now=time.time(); created=0; updated=0; errors=[]
        with self.store.transaction() as db:
            for position,record in enumerate(records):
                try:
                    entity=record['entity_type']; external_id=record['external_id']; fields=record.get('fields',{})
                    if entity not in ENTITY_TYPES or not external_id or not isinstance(fields,dict): raise ValueError('Invalid canonical record.')
                    item={'id':uuid.uuid4().hex,'connector_id':connector_id,'entity_type':entity,'external_id':external_id,
                          'fields':fields,'source_updated_at':record.get('source_updated_at'),'synced_at':now,
                          'ownership':record.get('ownership','connector')}
                    row=db.execute('SELECT id FROM connector_records WHERE connector_id=? AND entity_type=? AND external_id=?',
                                   (connector_id,entity,external_id)).fetchone()
                    if row:
                        item['id']=row['id']; db.execute('UPDATE connector_records SET synced_at=?,payload=? WHERE id=?',(now,json.dumps(item),item['id'])); updated+=1
                    else:
                        db.execute('INSERT INTO connector_records VALUES(?,?,?,?,?,?)',(item['id'],connector_id,entity,external_id,now,json.dumps(item))); created+=1
                except Exception as exc:
                    error={'position':position,'message':'Record failed canonical validation.','record':record}
                    errors.append(error); db.execute('INSERT INTO connector_dead_letters VALUES(?,?,?,?,?)',(uuid.uuid4().hex,connector_id,now,'validation',json.dumps(error)))
            state={'connector_id':connector_id,'cursor':cursor,'last_sync_at':now,'created':created,'updated':updated,'errors':len(errors)}
            db.execute('INSERT OR REPLACE INTO connector_states VALUES(?,?,?)',(connector_id,now,json.dumps(state)))
        return {**state,'error_items':errors}
    def records(self,connector_id,entity_type=None):
        self.configuration(connector_id)
        with self.store.reading() as db:
            if entity_type: rows=db.execute('SELECT payload FROM connector_records WHERE connector_id=? AND entity_type=? ORDER BY synced_at DESC',(connector_id,entity_type)).fetchall()
            else: rows=db.execute('SELECT payload FROM connector_records WHERE connector_id=? ORDER BY synced_at DESC',(connector_id,)).fetchall()
        return [json.loads(row[0]) for row in rows]
    def queue_write(self,connector_id,entity_type,external_id,operation,fields,approved_by):
        connector=self.configuration(connector_id)
        if connector.get('access_mode')!='read_write': raise Conflict('Connector is configured as read-only.')
        if entity_type not in ENTITY_TYPES or operation not in {'create','update','delete'}: raise Conflict('Unsupported connector write.')
        now=time.time(); action={'id':uuid.uuid4().hex,'connector_id':connector_id,'entity_type':entity_type,
            'external_id':external_id,'operation':operation,'fields':fields,'approved_by':approved_by,'status':'queued','created_at':now}
        with self.store.transaction() as db: db.execute('INSERT INTO connector_outbox VALUES(?,?,?,?,?)',(action['id'],connector_id,'queued',now,json.dumps(action)))
        return action
