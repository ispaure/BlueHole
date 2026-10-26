"""Blue Hole-owned immutable preparation, native gates and reviewed draft plans."""
from pathlib import Path
import sys
from uuid import uuid4

from build_manager import Phase, Plan

ROOT = Path(__file__).resolve().parents[1]


def make_plan(operation, target, backend, values, source, tools_env, origins, secrets):
    from Scripts.validation import suite_selection
    suite, pattern = values.get('suite', ''), values.get('pattern', '')
    suite_selection(suite, operation, target, pattern)
    if operation not in {'Check', 'Package', 'Prepare GitHub release', 'Reviewed GitHub draft'} or backend != 'Local':
        raise ValueError('Unsupported Blue Hole operation/backend.')
    revision = values.get('revision', 'working-tree')
    if revision not in {'', 'working-tree', 'HEAD'} or revision == 'HEAD' and source['dirty']:
        raise ValueError('Blue Hole validates this exact checkout; historical revisions need a separately registered checkout.')
    release = operation in {'Prepare GitHub release', 'Reviewed GitHub draft'}
    if release and not values.get('release_tag'):
        from Scripts.release_adapter import suggest_release_tag
        values = dict(values,release_tag=suggest_release_tag(source))
    if release and pattern:
        raise ValueError('Release acceptance cannot use a focused test pattern.')
    from Scripts.release_adapter import artifact_name
    run = ROOT / 'test-results/release' / uuid4().hex
    artifact = run / artifact_name()
    checks, inspection, native = (run / name for name in ('checks.json', 'inspection.json', 'native.json'))
    phases = []
    def validation(name, action, output, dependencies=(), extra=()):
        report = output.with_suffix('.xml')
        return Phase(name, (sys.executable, '-m', 'Scripts.validation', action, '--output', str(output),
                           '--junit', str(report), *extra), str(ROOT), timeout=600 if action == 'portable' else 300,
                     dependencies=dependencies, environment=tools_env, artifacts=(str(report), str(output)),
                     artifact_types={str(report): 'junit'}, effect='test')
    if suite != 'blender.integration':
        extra = ('--pattern', pattern) if pattern else ()
        phases.append(validation('portable-contracts', 'portable', checks, extra=extra))
    if operation == 'Check':
        if suite != 'portable.contracts':
            phases.append(validation('blender-integration', 'native', native,
                                     dependencies=tuple(phase.id for phase in phases)))
    else:
        phases.append(Phase('package', (sys.executable, 'Scripts/release_adapter.py', 'package', '--output', str(artifact),
            '--checks', str(checks)), str(ROOT), timeout=300, dependencies=('portable-contracts',), kind='build',
            environment=tools_env, artifacts=(str(artifact), str(artifact.with_suffix('.json'))), effect='build'))
        receipt_args = ('--receipt', str(artifact.with_suffix('.json')))
        phases.append(validation('package-inspection', 'inspect', inspection, ('package',), receipt_args))
        if release:
            phases.append(validation('blender-integration', 'native', native, ('package-inspection',), receipt_args))
            hosted = tools_env.get('BLUEHOLE_HOSTED_EVIDENCE', '')
            evidence = ('--checks', str(checks), *receipt_args, '--inspection', str(inspection), '--native', str(native))
            if hosted:
                evidence += ('--hosted', hosted)
            phases.append(validation('release-acceptance', 'acceptance', run / 'acceptance.json',
                                     ('portable-contracts', 'package-inspection', 'blender-integration'), evidence))
            candidate = run / 'candidate.json'
            phases.append(Phase('release-review', (sys.executable, 'Scripts/release_adapter.py', 'prepare', *evidence,
                '--tag', values['release_tag'], '--output', str(candidate)), str(ROOT), timeout=120,
                dependencies=('release-acceptance',), environment=tools_env, kind='inspect', effect='inspect',
                artifacts=(str(candidate),)))
            if operation == 'Reviewed GitHub draft':
                phases.append(Phase('github-draft', (sys.executable, '-m', 'Scripts.reviewed_release',
                    '--candidate', str(candidate), '--receipt', str(run / 'draft-receipt.json')), str(ROOT),
                    dependencies=('release-review',), environment=tools_env, timeout=300, kind='distribution',
                    effect='upload', provider='github', artifacts=(str(run / 'draft-receipt.json'),)))
    return Plan('Blue Hole', operation, dict(source, destination='ispaure/BlueHole', channel='alpha',
                test_suite=suite or 'full declared operation', focused_test_pattern=pattern, release_tag=values.get('release_tag','')), tuple(phases), str(ROOT / 'test-results/build-manager/workspace'),
                effect='test' if operation == 'Check' else 'build', secret_environment=secrets,
                settings=dict(values=tools_env, origins=dict(origins, BLUEHOLE_MANAGER_SOURCE='captured source identity')))
