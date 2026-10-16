"""Standalone catalogue, audiences, leads and portable imports."""
import csv
import io
from .store import Conflict

class StandaloneWorkspace:
    def __init__(self,store): self.store=store
    def import_leads(self,csv_text,mapping,source):
        reader=csv.DictReader(io.StringIO(csv_text))
        if not reader.fieldnames: raise Conflict('CSV file must include a header row.')
        allowed={'name','email','phone','product_interest','message','consent_status'}
        mapping=mapping or {name:name for name in reader.fieldnames if name in allowed}
        if any(target not in allowed for target in mapping.values()): raise Conflict('CSV mapping contains an unsupported lead field.')
        created=[]; errors=[]
        for number,row in enumerate(reader,2):
            payload={target:(row.get(source_name) or '').strip() for source_name,target in mapping.items()}
            payload.update(source=source,campaign_id=None,custom_fields={})
            payload.setdefault('consent_status','unknown')
            try: created.append(self.store.create_lead(payload))
            except Conflict as exc: errors.append({'row':number,'message':str(exc)})
        return {'created':len(created),'errors':errors,'lead_ids':[item['id'] for item in created]}
