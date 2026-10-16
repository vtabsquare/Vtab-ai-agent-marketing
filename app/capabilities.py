"""Capability-driven configuration shared by onboarding, workflows and connectors."""
from copy import deepcopy

DATA_MODES={'standalone','connected','hybrid'}
CHANNEL_MODES={'disabled','content_only','publishing_connected','fully_connected'}
KNOWN_CHANNELS=('discord','twitter','linkedin','instagram','facebook','whatsapp','email','web_export')
MODE_DESCRIPTIONS={
 'standalone':{'name':'Standalone','description':'Use website, manual records, files, forms and the built-in lead inbox without a CRM.','source_of_truth':'internal'},
 'connected':{'name':'Connected','description':'Use a connected CRM or business platform as the primary source while this workspace manages campaigns.','source_of_truth':'connector'},
 'hybrid':{'name':'Hybrid','description':'Combine connected systems with website and locally managed products, campaigns, assets and memory.','source_of_truth':'per_domain'}}
CHANNEL_DESCRIPTIONS={
 'disabled':'Hidden from campaigns; no content or external action is created.',
 'content_only':'Generate a channel-specific draft for review, copy or export without publishing.',
 'publishing_connected':'Generate, approve, schedule and publish through a verified account.',
 'fully_connected':'Publish and use supported metrics, comments and engagement capabilities.'}

def normalize_settings(settings):
    result=deepcopy(settings)
    result.setdefault('configuration_version',1); result.setdefault('data_mode','standalone')
    result.setdefault('website_url',''); result.setdefault('data_sources',[]); result.setdefault('connectors',[])
    result.setdefault('lead_destination','internal_inbox'); result.setdefault('feature_flags',{})
    existing=set(result.get('platforms',[])); channels=result.setdefault('channel_settings',{})
    for channel in KNOWN_CHANNELS:
        default='publishing_connected' if channel in existing else ('content_only' if channel=='web_export' else 'disabled')
        current=channels.setdefault(channel,{}); current.setdefault('mode',default); current.setdefault('enabled',current['mode']!='disabled')
        if channel in existing and current.get('mode')=='disabled':
            current.update(mode='publishing_connected',enabled=True)
    return result

def effective_capabilities(settings):
    from .connectors import CONNECTOR_TYPES
    settings=normalize_settings(settings)
    caps={'campaigns.create','campaigns.approve','content.generate','content.export','memory.campaign'}
    mode=settings['data_mode']
    if mode in {'standalone','hybrid'}: caps.update({'data.internal','leads.internal','imports.files'})
    if settings.get('website_url') or 'website' in settings.get('data_sources',[]): caps.update({'website.ingest','website.research'})
    enabled_connectors=[]
    for connector in settings.get('connectors',[]):
        if connector.get('enabled'):
            enabled_connectors.append(connector.get('id') or connector.get('type'))
            registered=CONNECTOR_TYPES.get(connector.get('type'),{})
            allowed=set(registered.get('capabilities',[]))
            caps.update(set(connector.get('capabilities',[])) & allowed or allowed)
    channels={}
    for name,configuration in settings['channel_settings'].items():
        channel_mode=configuration.get('mode','disabled')
        channels[name]={'mode':channel_mode,'description':CHANNEL_DESCRIPTIONS[channel_mode],'enabled':channel_mode!='disabled'}
        if channel_mode!='disabled': caps.add('content.channel.'+name)
        if channel_mode in {'publishing_connected','fully_connected'}: caps.add('publish.'+name)
        if channel_mode=='fully_connected': caps.update({'metrics.'+name,'engagement.'+name})
    return {'data_mode':mode,'mode':MODE_DESCRIPTIONS[mode],'capabilities':sorted(caps),'channels':channels,
            'connectors':enabled_connectors,'lead_destination':settings['lead_destination']}

def workflow_configuration_snapshot(settings):
    settings=normalize_settings(settings); effective=effective_capabilities(settings)
    return {'data_mode':settings['data_mode'],'configuration_version':settings['configuration_version'],
            'sources':list(settings.get('data_sources',[])),'source_connectors':effective['connectors'],
            'destinations':[{'channel':name,'state':item['mode']} for name,item in effective['channels'].items() if item['enabled']],
            'lead_destination':settings['lead_destination'],'capabilities':effective['capabilities'],'website_url':settings.get('website_url','')}
