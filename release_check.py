"""Run the repeatable release gate used before client packaging."""
from __future__ import annotations

import compileall
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(label, command, cwd=ROOT):
    print(f'\n[{label}] {" ".join(map(str, command))}')
    result = subprocess.run(command, cwd=cwd)
    if result.returncode: raise SystemExit(result.returncode)


def validate_configuration():
    from app.agents import AgentRegistry
    from app.workflow_registry import WorkflowRegistry
    agents = AgentRegistry(ROOT).snapshot({'provider':'demo','model':'deterministic-demo-v1','brand':{},'data_mode':'standalone'})
    workflows = WorkflowRegistry(ROOT).workflows
    json.loads((ROOT / 'config' / 'prompts.json').read_text(encoding='utf-8'))
    if not agents['agents'] or not workflows: raise SystemExit('Configuration registries are empty.')
    print(f'[configuration] {len(agents["agents"])} agent roles and {len(workflows)} workflow definitions validated')


def main():
    validate_configuration()
    if not compileall.compile_dir(ROOT / 'app', quiet=1): raise SystemExit('Python compilation failed.')
    print('[python] application modules compiled')
    run('backend tests', [sys.executable, '-m', 'pytest', '-q'])
    node = os.environ.get('MARKETING_NODE') or shutil.which('node')
    if not node: raise SystemExit('Node.js is required for the frontend release gate.')
    run('frontend API tests', [node, '--test', 'api.test.mjs'], ROOT / 'frontend')
    run('frontend production build', [node, 'build.mjs'], ROOT / 'frontend')
    with tempfile.TemporaryDirectory() as folder:
        from app.main import create_app
        app = create_app(folder, start_worker=False)
        versions = app.state.operations.diagnostics()['schema_versions']
        if not versions or versions[-1] != 8: raise SystemExit('Fresh database did not reach schema version 8.')
        app.state.store.close()
    print('\nRELEASE CHECK PASSED')


if __name__ == '__main__': main()
