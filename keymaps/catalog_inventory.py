"""Deterministic, Blender-independent catalog inventory and provenance."""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

TABLES = ('categories', 'sections', 'events', 'commands', 'assignments', 'suppressions')


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=False).encode()).hexdigest()


def read_catalog(path):
    """Assemble files for inspection; runtime validation remains authoritative."""
    path = Path(path)
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if 'storage_version' not in manifest:
        return manifest, {path.name: sha256(path.read_bytes()).hexdigest()}
    catalog = {key: manifest[key] for key in ('schema_version', 'catalog_version', 'base')}
    catalog.update({table: dict(manifest.get(table, {})) for table in TABLES})
    sources = {path.name: sha256(path.read_bytes()).hexdigest()}
    for category, relative in sorted(manifest['section_files'].items()):
        source = path.parent / relative
        if source.resolve().parent != (path.parent / (path.stem + '-sections')).resolve():
            raise ValueError('Section outside catalog directory')
        part = json.loads(source.read_text(encoding='utf-8'))
        catalog['categories'][category] = part['definition']
        for table in TABLES[1:]:
            if catalog[table].keys() & part[table].keys():
                raise ValueError(f'Duplicate {table} identifiers in {relative}')
            catalog[table].update(part[table])
        sources[relative] = sha256(source.read_bytes()).hexdigest()
    return catalog, sources


def assignment_semantics(catalog, id_):
    row = catalog['assignments'][id_]
    command = catalog['commands'][row['command']]
    return {'scope': row['scope'], 'event': catalog['events'][row['event']],
            'command': {k: v for k, v in command.items() if k != 'label'},
            'order': row['order']}


def inventory(catalog, sources=None):
    chains = defaultdict(list)
    duplicates = defaultdict(list)
    providers = Counter()
    for id_, row in sorted(catalog['assignments'].items(), key=lambda item: item[1]['order']):
        semantics = assignment_semantics(catalog, id_)
        if row.get('dispatch_group'):
            chains[row['dispatch_group']].append({'id': id_, 'signature': digest(semantics), **semantics})
        duplicates[digest({k: v for k, v in semantics.items() if k != 'order'})].append(id_)
        providers[catalog['commands'][row['command']].get('provider', 'Blender')] += 1
    return {'inventory_version': 1, 'catalog_digest': digest(catalog),
            'base': catalog['base'], 'sources': sources or {},
            'counts': {table: len(catalog[table]) for table in TABLES},
            'providers': dict(sorted(providers.items())), 'dispatch_chains': dict(chains),
            'duplicate_candidates': [ids for ids in duplicates.values() if len(ids) > 1]}
