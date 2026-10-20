from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


class Brand(Contract):
    name: str = Field(min_length=1, max_length=120)
    product: str = Field(min_length=1, max_length=300)
    price: str = Field(min_length=1, max_length=200)
    tone: str = Field(min_length=1, max_length=200)
    facts: str = Field(default="", max_length=4000)

class ChannelSetting(Contract):
    mode: Literal['disabled','content_only','publishing_connected','fully_connected'] = 'disabled'
    enabled: bool = False

class ConnectorSetting(Contract):
    id: str = Field(min_length=1,max_length=100,pattern=r'^[a-zA-Z0-9._-]+$')
    type: str = Field(min_length=1,max_length=80,pattern=r'^[a-zA-Z0-9._-]+$')
    enabled: bool = False
    access_mode: Literal['read_only','read_write'] = 'read_only'
    capabilities: list[str] = Field(default_factory=list,max_length=50)
    ownership_domains: list[Literal['contacts','accounts','products','segments','interactions','conversions','consent']] = Field(default_factory=list,max_length=20)
    field_mapping: dict[str,str] = Field(default_factory=dict)


class SettingsInput(Contract):
    provider: Literal["demo", "gemini"] = "demo"
    model: str = Field(default="", max_length=160, pattern=r"^[a-zA-Z0-9._/-]*$")
    api_key: str | None = Field(default=None, max_length=300)
    brand: Brand
    social_keys: dict[str, str] = Field(default_factory=dict)
    publishing_mode: Literal['simulation', 'live'] = 'simulation'
    platforms: list[Literal['discord', 'twitter', 'linkedin', 'facebook', 'instagram', 'whatsapp']] = Field(default_factory=list)
    image_provider: Literal['template', 'pollinations', 'huggingface'] = 'template'
    hf_model: str = Field(default='black-forest-labs/FLUX.1-schnell', max_length=200, pattern=r'^[a-zA-Z0-9._/-]+$')
    hf_provider: str = Field(default='auto', max_length=80, pattern=r'^[a-zA-Z0-9_-]+$')
    configuration_version: int = Field(default=1,ge=1)
    data_mode: Literal['standalone','connected','hybrid'] = 'standalone'
    website_url: str = Field(default='',max_length=2000)
    data_sources: list[Literal['website','manual','csv','excel','google_sheets','webhook','internal_forms']] = Field(default_factory=list,max_length=20)
    connectors: list[ConnectorSetting] = Field(default_factory=list,max_length=50)
    lead_destination: Literal['internal_inbox','email','csv_export','webhook','connector'] = 'internal_inbox'
    channel_settings: dict[str,ChannelSetting] = Field(default_factory=dict)
    feature_flags: dict[str,bool] = Field(default_factory=dict)


class Brief(Contract):
    title: str = Field(min_length=1, max_length=120)
    audience: str = Field(min_length=1, max_length=500)
    goal: str = Field(min_length=1, max_length=500)
    instructions: str = Field(default="", max_length=2000)
    checkpoint: Literal['none', 'creative', 'strategy'] = 'none'
    destinations: list[str] = Field(default_factory=list,max_length=20)
    audience_id: str | None = Field(default=None,max_length=100)
    schedule_at: float | None = Field(default=None,ge=0)
    workflow_id: str = Field(default='campaign.v1',max_length=100,pattern=r'^[a-zA-Z0-9._-]+$')


class InputAnswer(Contract):
    request_id: str = Field(min_length=1, max_length=100)
    answer: str = Field(min_length=1, max_length=2000)

class WebsiteScanRequest(Contract):
    url: str = Field(min_length=8,max_length=2000)
    max_pages: int = Field(default=12,ge=1,le=25)

class KnowledgeDecision(Contract):
    status: Literal['approved','rejected','superseded']
    note: str = Field(default='',max_length=1000)

class CatalogItemInput(Contract):
    kind: Literal['product','service','offer'] = 'product'
    name: str = Field(min_length=1,max_length=200)
    description: str = Field(default='',max_length=4000)
    price: str = Field(default='',max_length=120)
    active: bool = True
    source_url: str = Field(default='',max_length=2000)
    custom_fields: dict[str,str] = Field(default_factory=dict)

class AudienceInput(Contract):
    name: str = Field(min_length=1,max_length=160)
    description: str = Field(min_length=1,max_length=3000)
    region: str = Field(default='',max_length=200)
    language: str = Field(default='en',max_length=40)
    traits: list[str] = Field(default_factory=list,max_length=50)

class LeadInput(Contract):
    name: str = Field(default='',max_length=200)
    email: str = Field(default='',max_length=320)
    phone: str = Field(default='',max_length=80)
    source: str = Field(default='manual',max_length=120)
    campaign_id: str | None = Field(default=None,max_length=100)
    product_interest: str = Field(default='',max_length=500)
    message: str = Field(default='',max_length=4000)
    consent_status: Literal['unknown','granted','denied','withdrawn'] = 'unknown'
    custom_fields: dict[str,str] = Field(default_factory=dict)

class LeadUpdate(Contract):
    status: Literal['new','contacted','qualified','proposal_sent','won','lost','unqualified'] | None = None
    owner: str | None = Field(default=None,max_length=160)
    follow_up_at: float | None = Field(default=None,ge=0)
    note: str | None = Field(default=None,max_length=2000)
    consent_status: Literal['unknown','granted','denied','withdrawn'] | None = None

class LeadImportRequest(Contract):
    csv_text: str = Field(min_length=1,max_length=2_000_000)
    mapping: dict[str,str] = Field(default_factory=dict)
    source: str = Field(default='csv_import',max_length=120)

class MemoryInput(Contract):
    scope: str = Field(min_length=1,max_length=200,pattern=r'^(client|performance|agent\.[a-z_]+|campaign\.[a-f0-9]+)$')
    memory_type: str = Field(min_length=1,max_length=100,pattern=r'^[a-zA-Z0-9._-]+$')
    content: str = Field(min_length=1,max_length=12000)
    source: str = Field(min_length=1,max_length=120)
    source_id: str | None = Field(default=None,max_length=200)
    confidence: float = Field(default=0.5,ge=0,le=1)
    status: Literal['candidate','approved','rejected','superseded','expired'] = 'candidate'
    sensitivity: Literal['public','internal','confidential','personal'] = 'internal'
    tags: list[str] = Field(default_factory=list,max_length=50)
    expires_at: float | None = Field(default=None,ge=0)
    prompt_version: str | None = Field(default=None,max_length=120)
    model_version: str | None = Field(default=None,max_length=160)
    supersedes_id: str | None = Field(default=None,max_length=100)

class MemoryDecision(Contract):
    status: Literal['approved','rejected','superseded']
    note: str = Field(default='',max_length=1000)

class LandingPageInput(Contract):
    slug: str = Field(min_length=1,max_length=100)
    title: str = Field(min_length=1,max_length=200)
    eyebrow: str = Field(default='',max_length=120)
    body: str = Field(min_length=1,max_length=5000)
    cta_label: str = Field(default='Request details',min_length=1,max_length=100)
    campaign_id: str | None = Field(default=None,max_length=100)
    product_interest: str = Field(default='',max_length=500)

class UTMRequest(Contract):
    url: str = Field(min_length=8,max_length=2000)
    source: str = Field(min_length=1,max_length=120)
    medium: str = Field(min_length=1,max_length=120)
    campaign: str = Field(min_length=1,max_length=200)
    content: str = Field(default='',max_length=200)

class MetricEventInput(Contract):
    event_type: Literal['page_view','cta_click','form_start','form_submit','lead_qualified','conversion']
    source: str = Field(min_length=1,max_length=120)
    campaign_id: str | None = Field(default=None,max_length=100)
    metadata: dict[str,str|int|float|bool] = Field(default_factory=dict)

class ExperimentVariant(Contract):
    id: str = Field(min_length=1,max_length=80,pattern=r'^[a-zA-Z0-9._-]+$')
    name: str = Field(min_length=1,max_length=160)
    description: str = Field(min_length=1,max_length=1000)

class ExperimentInput(Contract):
    name: str = Field(min_length=1,max_length=200)
    campaign_id: str | None = Field(default=None,max_length=100)
    hypothesis: str = Field(min_length=1,max_length=2000)
    metric: str = Field(min_length=1,max_length=120)
    stop_rule: str = Field(min_length=1,max_length=1000)
    variants: list[ExperimentVariant] = Field(min_length=2,max_length=10)

class ExperimentResultInput(Contract):
    variant: str = Field(min_length=1,max_length=80)
    exposures: int = Field(ge=0)
    conversions: int = Field(ge=0)

class ConnectorRecord(Contract):
    entity_type: Literal['contact','account','product','segment','interaction','conversion','consent']
    external_id: str = Field(max_length=300)
    fields: dict[str,str|int|float|bool|None] = Field(default_factory=dict)
    source_updated_at: float | None = Field(default=None,ge=0)
    ownership: Literal['connector','local','shared'] = 'connector'

class ConnectorSyncInput(Contract):
    records: list[ConnectorRecord] = Field(default_factory=list,max_length=1000)
    cursor: str | None = Field(default=None,max_length=1000)

class ConnectorWriteInput(Contract):
    entity_type: Literal['contact','account','product','segment','interaction','conversion','consent']
    external_id: str = Field(default='',max_length=300)
    operation: Literal['create','update','delete']
    fields: dict[str,str|int|float|bool|None] = Field(default_factory=dict)
    approved_by: str = Field(min_length=1,max_length=160)

class LoginInput(Contract):
    email: str = Field(min_length=1,max_length=320)
    password: str = Field(min_length=12,max_length=300)

class WorkspaceUserInput(Contract):
    email: str = Field(min_length=3,max_length=320,pattern=r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
    name: str = Field(min_length=1,max_length=160)
    role: Literal['owner','admin','editor','analyst','viewer'] = 'editor'
    password: str = Field(min_length=12,max_length=300)

class UserStateInput(Contract):
    name: str | None = Field(default=None,min_length=1,max_length=160)
    role: Literal['owner','admin','editor','analyst','viewer'] | None = None
    active: bool | None = None


class HumanQuestion(Contract):
    question: str = Field(min_length=1, max_length=500)
    reason: str = Field(min_length=1, max_length=700)


class AgentOutput(Contract):
    input_request: HumanQuestion | None = None


class Decision(Contract):
    content_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    note: str = Field(default="", max_length=1000)


class Revision(Contract):
    note: str = Field(min_length=1, max_length=1000)
    content_hash: str = Field(pattern=r"^[a-f0-9]{64}$")


class Finding(Contract):
    text: str = Field(min_length=1, max_length=1200)
    source_ref: str = Field(min_length=1, max_length=200)
    source_url: str | None = Field(default=None, max_length=2000)
    source_title: str | None = Field(default=None, max_length=500)
    retrieved_at: str | None = Field(default=None, max_length=40)
    confidence: float | None = Field(default=None, ge=0, le=1)


class Research(AgentOutput):
    findings: list[Finding] = Field(min_length=1, max_length=5)
    limitations: str = Field(min_length=1, max_length=1200)


class Strategy(AgentOutput):
    summary: str = Field(min_length=1, max_length=1600)
    content_angle: str = Field(min_length=1, max_length=500)
    success_measure: str = Field(min_length=1, max_length=500)


class ChannelVariant(Contract):
    channel: str = Field(min_length=1,max_length=80)
    headline: str = Field(default='',max_length=250)
    body: str = Field(min_length=1,max_length=4000)
    call_to_action: str = Field(default='',max_length=300)

class Writing(AgentOutput):
    headline: str = Field(min_length=1, max_length=250)
    caption: str = Field(min_length=1, max_length=3500)
    product_claim: str = Field(min_length=1, max_length=300)
    price_claim: str = Field(min_length=1, max_length=200)
    call_to_action: str = Field(min_length=1, max_length=300)
    variants: list[ChannelVariant] = Field(default_factory=list,max_length=20)


class Creative(AgentOutput):
    headline: str = Field(min_length=1, max_length=100)
    art_direction: str = Field(min_length=1, max_length=700, description="A highly detailed, professional visual prompt for the marketing photograph. DO NOT include text/typography.")
    primary_hex: str = Field(default="#172554", pattern=r"^#[0-9a-fA-F]{6}$", description="A dominant background hex color code matching the vibe of the campaign (e.g., #1A1A1A).")
    accent_hex: str = Field(default="#38bdf8", pattern=r"^#[0-9a-fA-F]{6}$", description="A contrasting accent hex color code for highlights/buttons (e.g., #FFC837).")
    font_name: str = Field(default="Arial", max_length=80, pattern=r"^[a-zA-Z0-9 -]+$", description="The exact name of a Google Font that matches the campaign's personality (e.g., 'Playfair Display', 'Oswald', 'Montserrat', 'Bebas Neue', 'Pacifico').")
    layout_style: Literal['split', 'minimal', 'full-bleed'] = Field(default='split', description="The structural layout of the ad.")


class Review(AgentOutput):
    verdict: Literal["pass", "revise"]
    findings: list[str] = Field(max_length=8)
    summary: str = Field(min_length=1, max_length=1000)


class Manager(AgentOutput):
    recommendation: Literal["request_approval", "revise"]
    summary: str = Field(min_length=1, max_length=1400)
    concerns: list[str] = Field(max_length=8)


class Analytics(AgentOutput):
    interpretation: str = Field(min_length=1, max_length=1200)
    limitations: str = Field(min_length=1, max_length=700)


class Optimization(AgentOutput):
    hypothesis: str = Field(min_length=1, max_length=1000)
    proposed_change: str = Field(min_length=1, max_length=1000)
    stop_rule: str = Field(min_length=1, max_length=500)


class Engagement(AgentOutput):
    category: str = Field(min_length=1, max_length=120)
    draft_reply: str = Field(min_length=1, max_length=700)
    requires_human: bool


SCHEMAS = {"research": Research, "strategy": Strategy, "writing": Writing,
           "creative": Creative, "brand_review": Review, "manager": Manager,
           "analytics": Analytics, "optimization": Optimization, "engagement": Engagement}
