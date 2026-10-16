"""Task graph: independent siblings run concurrently; required inputs gate dependents."""
import time
ROLES = ['research', 'strategy', 'writing', 'creative', 'brand_review', 'manager',
         'publishing', 'analytics', 'optimization', 'engagement']
DEPENDENCIES = {'research': [], 'strategy': ['research'], 'writing': ['strategy'],
                'creative': ['strategy'], 'brand_review': ['writing', 'creative'],
                'manager': ['brand_review'], 'publishing': ['manager'],
                'analytics': ['publishing'], 'optimization': ['analytics'], 'engagement': ['publishing']}
NAMES = {'research': 'Research Bot', 'strategy': 'Strategy Bot', 'writing': 'Writer Bot',
         'creative': 'Creative Bot', 'brand_review': 'Brand Guardian', 'manager': 'Marketing Manager',
         'publishing': 'Publisher Bot', 'analytics': 'Analytics Bot', 'optimization': 'Optimizer Bot',
         'engagement': 'Community Bot', 'local-owner': 'You', 'controller': 'Marketing Manager'}
START_MESSAGES = {
    'research': 'I am checking the supplied brief, audience and approved brand facts.',
    'strategy': 'Research received. I am turning the findings into a campaign plan.',
    'writing': 'Strategy received. I am drafting the copy using the approved product facts.',
    'creative': 'Strategy received. I am preparing the visual direction while Writer Bot works on the copy.',
    'brand_review': 'Both copy and creative are ready. I am checking claims, price and brand consistency.',
    'manager': 'Brand review is ready. I am checking the complete package before asking for your decision.',
    'publishing': 'Your approval is recorded. I am submitting the exact authorized version to its selected destination.',
    'analytics': 'Publication is confirmed. I am collecting the available performance evidence.',
    'optimization': 'Analytics received. I am preparing an evidence-based proposal for the next experiment.',
    'engagement': 'The publication is confirmed. I am preparing a reply to the sample audience enquiry.'
}


def nodes():
    return {role: {'state': 'PENDING', 'attempt': 0, 'lease': None, 'lease_until': 0,
                   'not_before': 0, 'generation': 0, 'error': None} for role in ROLES}

def campaign_roles(c):
    return c.get('snapshot',{}).get('workflow',{}).get('roles',ROLES)

def campaign_dependencies(c):
    return c.get('snapshot',{}).get('workflow',{}).get('dependencies',DEPENDENCIES)


def ready(c, role):
    node = c['nodes'][role]
    if node['state'] not in {'PENDING', 'RETRY_SCHEDULED', 'SCHEDULED_WAIT'}:
        return False
    if role not in campaign_roles(c): return False
    if not all(c['nodes'][dep]['state'] == 'ACCEPTED' for dep in campaign_dependencies(c)[role]):
        return False
    return role != 'publishing' or bool(c.get('approval'))


def refresh_state(c):
    if c['state'] == 'CANCELLED':
        return
    states = [c['nodes'][role]['state'] for role in campaign_roles(c)]
    c['stage'] = sum(state == 'ACCEPTED' for state in states)
    if c['stage'] == len(campaign_roles(c)):
        c['state'] = 'COMPLETED'
    elif 'RUNNING' in states:
        c['state'] = 'RUNNING'
    elif any(ready(c, role) and c['nodes'][role]['not_before'] <= time.time() for role in campaign_roles(c)):
        c['state'] = 'QUEUED'
    elif any(q['status'] == 'OPEN' and q['kind'] == 'approval' for q in c['input_requests']):
        c['state'] = 'AWAITING_APPROVAL'
    elif 'WAITING_INPUT' in states:
        c['state'] = 'WAITING_INPUT'
    elif 'BLOCKED' in states:
        c['state'] = 'BLOCKED'
    elif 'SCHEDULED_WAIT' in states:
        c['state'] = 'SCHEDULED_WAIT'
    elif 'RETRY_SCHEDULED' in states:
        c['state'] = 'RETRY_SCHEDULED'
    else:
        c['state'] = 'QUEUED'
