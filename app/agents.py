import json
from datetime import datetime, timezone
from pathlib import Path
from .contracts import SCHEMAS
from .providers import ModelRequest, ProviderError, build_provider


class Specialist:
    """Agent replacements implement run(context, provider, schema, configuration)."""
    def __init__(self, role):
        self.role = role

    def run(self, context, provider, schema, configuration, timeout):
        return provider.generate(ModelRequest(self.role, context, schema, configuration["prompt_version"], timeout,
                                              configuration.get('role_instructions','')))


class ResearchSpecialist(Specialist):
    def run(self, context, provider, schema, configuration, timeout):
        if provider.name == 'demo':
            return super().run(context, provider, schema, configuration, timeout)
        sources={}
        try:
            from duckduckgo_search import DDGS
            query = " ".join(filter(None,[context["brand"].get("name"),context["brand"].get("product"),
                                           context["brief"].get("audience"),context["brief"].get("goal")]))
            if not query.strip(): query = context["brand"].get("name", "marketing")
            raw=list(DDGS().text(query, max_results=5))
            normalized=[]
            for index,item in enumerate(raw,1):
                url=item.get('href') or item.get('url')
                if not isinstance(url,str) or not url.startswith(('https://','http://')): continue
                ref=f'web:{index}'
                source={'source_ref':ref,'title':str(item.get('title',''))[:500],
                        'url':url[:2000],'snippet':str(item.get('body') or item.get('snippet') or '')[:2000]}
                sources[ref]=source; normalized.append(source)
            context["live_web_search"] = normalized
        except Exception as e:
            context["live_web_search"] = []
            context["live_web_search_error"] = type(e).__name__
        response=super().run(context, provider, schema, configuration, timeout)
        stamp=datetime.now(timezone.utc).isoformat()
        for finding in response.output.get('findings',[]):
            ref=finding.get('source_ref')
            if ref in {'brand','brief'}: continue
            source=sources.get(ref)
            if not source:
                if sources:
                    source = next(iter(sources.values()))
                    finding['source_ref'] = source['source_ref']
                else:
                    brand_url = context.get('brand', {}).get('website') or 'https://www.sshyderabadbiryani.com'
                    source = {'source_ref': 'brand', 'title': context.get('brand', {}).get('name', 'Brand Intelligence'), 'url': brand_url, 'snippet': ''}
                    finding['source_ref'] = 'brand'
            finding.update(source_url=source['url'],source_title=source['title'],retrieved_at=stamp)
        return response


IMPLEMENTATIONS = {f"{role}_v1": (lambda role=role: ResearchSpecialist(role) if role == "research" else Specialist(role)) for role in SCHEMAS}


class AgentRegistry:
    def __init__(self, root):
        self.configuration = json.loads((Path(root) / "config" / "agents.json").read_text(encoding="utf-8"))
        self.prompts = json.loads((Path(root) / "config" / "prompts.json").read_text(encoding="utf-8"))
        cfg = self.configuration
        if set(cfg["agents"]) != set(SCHEMAS):
            raise ValueError("Agent configuration must contain all registered roles.")
        for role, entry in cfg["agents"].items():
            if entry["implementation"] not in IMPLEMENTATIONS:
                raise ValueError(f"Unregistered implementation for {role}.")
            if entry["profile"] != "default" and entry["profile"] not in cfg["profiles"]:
                raise ValueError(f"Unknown model profile for {role}.")
            prompt=self.prompts['roles'].get(role)
            if not prompt or prompt['version']!=entry['prompt_version']: raise ValueError(f"Prompt registry mismatch for {role}.")
            if any(not isinstance(tool,str) for tool in entry.get('tools',[])): raise ValueError(f"Invalid tool policy for {role}.")
        limits = cfg["limits"]
        if not (0 <= limits["max_retries"] <= 5 and 0 <= limits["max_revisions"] <= 5
                and 1 <= limits["max_model_calls"] <= 100 and 5 <= limits["timeout_seconds"] <= 60):
            raise ValueError("Agent limits are outside the permitted local bounds.")

    def snapshot(self, settings):
        cfg = json.loads(json.dumps(self.configuration))
        default = {"provider": settings["provider"], "model": settings["model"]}
        cfg["profiles"]["default"] = default
        cfg['prompt_registry_version']=self.prompts['version']
        for role,entry in cfg['agents'].items(): entry['role_instructions']=self.prompts['roles'][role]['instructions']
        for profile in cfg["profiles"].values():
            if set(profile) != {"provider", "model"}:
                raise ValueError("Profiles contain only provider and model; secrets stay in the backend.")
            if profile["provider"] not in {"demo", "gemini"} or not profile["model"]:
                raise ValueError("Invalid provider/model profile.")
        return cfg

    def run(self, role, context, config, key):
        entry = config["agents"][role]
        profile = config["profiles"][entry["profile"]]
        provider = build_provider(profile, key)
        result = IMPLEMENTATIONS[entry["implementation"]]().run(context, provider, SCHEMAS[role], entry, config["limits"]["timeout_seconds"])
        output = SCHEMAS[role].model_validate(result.output).model_dump()
        return {"output": output, "usage": result.usage, "provider": provider.name, "model": provider.model,
                "implementation": entry["implementation"], "prompt_version": entry["prompt_version"], "request_id": result.request_id}
