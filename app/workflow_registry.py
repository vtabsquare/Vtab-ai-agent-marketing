"""Versioned workflow definitions with strict DAG and capability validation."""
import json
from pathlib import Path
from .workflow import ROLES

class WorkflowRegistry:
    def __init__(self,root):
        data=json.loads((Path(root)/'config'/'workflows.json').read_text(encoding='utf-8'))
        self.version=data['version']; self.default=data['default']; self.workflows=data['workflows']
        if self.default not in self.workflows: raise ValueError('Default workflow is not registered.')
        for workflow_id,definition in self.workflows.items(): self._validate(workflow_id,definition)

    def _validate(self,workflow_id,definition):
        roles=definition.get('roles',[]); dependencies=definition.get('dependencies',{})
        if not roles or len(roles)!=len(set(roles)) or any(role not in ROLES for role in roles):
            raise ValueError('Workflow '+workflow_id+' contains invalid roles.')
        if set(dependencies)!=set(roles): raise ValueError('Workflow '+workflow_id+' must define dependencies for every role.')
        if any(dep not in roles for role in roles for dep in dependencies[role]): raise ValueError('Workflow '+workflow_id+' has an unknown dependency.')
        visiting=set(); visited=set()
        def visit(role):
            if role in visiting: raise ValueError('Workflow '+workflow_id+' contains a dependency cycle.')
            if role in visited: return
            visiting.add(role)
            for dep in dependencies[role]: visit(dep)
            visiting.remove(role); visited.add(role)
        for role in roles: visit(role)

    def get(self,workflow_id=None):
        workflow_id=workflow_id or self.default
        if workflow_id not in self.workflows: raise ValueError('Unknown workflow definition.')
        return {'id':workflow_id,'registry_version':self.version,**json.loads(json.dumps(self.workflows[workflow_id]))}

    def available(self,capabilities):
        available=set(capabilities); result=[]
        for workflow_id,definition in self.workflows.items():
            missing=sorted(set(definition.get('required_capabilities',[]))-available)
            result.append({'id':workflow_id,'name':definition['name'],'description':definition['description'],
                           'available':not missing,'missing_capabilities':missing})
        return result
