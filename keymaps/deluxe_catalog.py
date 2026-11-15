"""Human-editable section files with whole-catalog validation and recovery.

The manifest is published last. A durable transaction marker prevents loading a
mixed generation after an interrupted save; ProfileStore retains a full recovery
snapshot. Only paths declared by this catalog may be replaced or retired.
"""

from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

from ..Lib.commonUtils.persistence.atomic import atomic_write_bytes
from ..Lib.commonUtils.runtime.operations import MutationIncomplete
from .deluxe_schema import (ProfileError, TABLES, identifier, independent_commands,
                            record, require, validate_catalog)


def transaction_path(path):
    return Path(path).with_suffix('.transaction.json')


def read_json(path):
    path = Path(path)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f'Duplicate JSON key {key!r}')
            result[key] = value
        return result
    def constant(value):
        raise ProfileError(f'Invalid JSON number {value}')
    try:
        return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique,
                          parse_constant=constant)
    except json.JSONDecodeError as error:
        raise ProfileError(f'{path.name}:{error.lineno}:{error.colno}: {error.msg}') from error
    except (OSError, UnicodeError, ValueError, RecursionError) as error:
        raise ProfileError(f'{path.name}: {error}') from error


def section_paths(path, manifest):
    path = Path(path)
    require(isinstance(manifest, dict), f'{path.name}: expected a JSON object')
    files = manifest.get('section_files', {})
    require(isinstance(files, dict), f'{path.name}: section_files must be an object')
    result = {}
    for category, name in files.items():
        require(identifier(category), f'{path.name}: invalid section ID {category!r}')
        expected = f'{path.stem}-sections/{category}.json'
        require(name == expected, f'{path.name}: section_files[{category!r}] must be {expected!r}')
        target = path.parent / expected
        require(not target.is_symlink() and not target.parent.is_symlink(),
                f'{target.name}: section files cannot be symbolic links')
        result[category] = target
    return result


def load(path, *, allow_transaction=False, migrate=True):
    path = Path(path)
    initial_revision = revision(path)
    require(allow_transaction or not transaction_path(path).exists(),
            f'{path.name}: interrupted save; reload the recovery copy or save the recovered setup')
    data = read_json(path)
    require(isinstance(data, dict), f'{path.name}: expected a JSON object')
    origins = {}
    if 'storage_version' in data:
        try:
            record(data, ('storage_version', 'schema_version', 'catalog_version', 'base',
                          'section_files', 'events', 'commands'))
            require(type(data['storage_version']) is int and data['storage_version'] == 1,
                    'Unsupported catalog storage version')
            paths = section_paths(path, data)
        except ProfileError as error:
            raise ProfileError(f'{path.name}: {error}') from error
        catalog = {key: data[key] for key in ('schema_version', 'catalog_version', 'base')}
        catalog.update({table: data.get(table, {}) for table in TABLES})
        for table in ('events', 'commands'):
            require(isinstance(catalog[table], dict), f'{path.name}: {table} must be an object')
        for category, source in paths.items():
            part = read_json(source)
            try:
                record(part, ('category', 'definition', *TABLES[1:]))
                require(part['category'] == category, 'Section ID does not match the master file')
                catalog['categories'][category] = part['definition']
                origins['categories', category] = source
                for table in TABLES[1:]:
                    rows = part[table]
                    require(isinstance(rows, dict), f'{table} must be an object')
                    for id_, row in rows.items():
                        require(id_ not in catalog[table], f'Duplicate {table} ID {id_!r}')
                        catalog[table][id_] = row
                        origins[table, id_] = source
                for id_, row in part['sections'].items():
                    require(isinstance(row, dict) and row.get('category') == category,
                            f'sections[{id_!r}] must belong to {category!r}')
                for table in ('assignments', 'suppressions'):
                    for id_, row in part[table].items():
                        require(isinstance(row, dict) and identifier(row.get('section'))
                                and row['section'] in part['sections'],
                                f'{table}[{id_!r}] references a subsection outside this file')
            except ProfileError as error:
                raise ProfileError(f'{source.name}: {error}') from error
    else:
        catalog = data  # Legacy single-file catalogs migrate on the next save.
    try:
        validate_catalog(catalog)
    except ProfileError as error:
        location = getattr(error, 'location', None)
        source = origins.get(location, path)
        line = ''
        if location:
            needle = json.dumps(location[1]) + ':'
            for number, value in enumerate(source.read_text(encoding='utf-8').splitlines(), 1):
                if needle in value:
                    line = f':{number}'
                    break
        raise ProfileError(f'{source.name}{line}: {error}') from error
    require(revision(path) == initial_revision, f'{path.name}: files changed while validating; reload again')
    require(allow_transaction or not transaction_path(path).exists(), f'{path.name}: save in progress; reload again')
    return independent_commands(catalog) if migrate else catalog


def split(path, catalog):
    """Store owned commands with their bindings; keep shared events in the master."""
    path = Path(path)
    validate_catalog(catalog)
    master = {key: catalog[key] for key in ('schema_version', 'catalog_version', 'base')}
    master = {'storage_version': 1, **master, 'section_files': {}, 'events': {}, 'commands': {}}
    parts = {}
    for id_, row in catalog['categories'].items():
        master['section_files'][id_] = f'{path.stem}-sections/{id_}.json'
        parts[id_] = {'category': id_, 'definition': row, **{table: {} for table in TABLES[1:]}}
    owners = {table: defaultdict(set) for table in ('events', 'commands')}
    for id_, row in catalog['sections'].items():
        parts[row['category']]['sections'][id_] = row
    for table in ('assignments', 'suppressions'):
        for id_, row in catalog[table].items():
            category = catalog['sections'][row['section']]['category']
            parts[category][table][id_] = row
            for field, reference in (('event', 'events'), ('command', 'commands'), ('replacement', 'commands')):
                if field in row:
                    owners[reference][row[field]].add(category)
    for table in ('events', 'commands'):
        for id_, row in catalog[table].items():
            categories = owners[table][id_]
            target = parts[next(iter(categories))] if len(categories) == 1 else master
            target[table][id_] = row
    return {path: master, **{path.parent / master['section_files'][id_]: part
                            for id_, part in parts.items()}}


def encode(data):
    # One complete record per line makes IDs and Git diffs easy to find.
    def dump(value):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    lines = []
    for key, value in data.items():
        if isinstance(value, dict) and value:
            formatted = '{\n' + ',\n'.join(f'    {dump(id_)}: {dump(row)}' for id_, row in value.items()) + '\n  }'
        else:
            formatted = dump(value)
        lines.append(f'  {dump(key)}: {formatted}')
    return ('{\n' + ',\n'.join(lines) + '\n}\n').encode('utf-8')


def revision(path):
    """Include every managed section, even with a broken master or missing file."""
    path = Path(path)
    paths = [path, transaction_path(path)]
    folder = path.parent / (path.stem + '-sections')
    try:
        paths += sorted(folder.glob('*.json'))
        digest = sha256()
        for source in paths:
            digest.update(str(source.relative_to(path.parent)).encode())
            digest.update(source.read_bytes() if source.exists() else b'<missing>')
        return digest.digest()
    except OSError:
        return 'unreadable'


def publish(path, catalog, previous, expected_revision):
    path = Path(path)
    documents = split(path, catalog)
    known = set(split(path, previous))
    marker = transaction_path(path)
    try:
        original_manifest = read_json(path)
        known.update(section_paths(path, original_manifest).values())
    except ProfileError:
        pass  # The validated recovery snapshot supplies owned paths.
    for source in documents:
        require(not source.is_symlink() and not source.parent.is_symlink(),
                f'{source.name}: refusing to replace a symbolic link')
        require(source in known or not source.exists(), f'{source.name}: an unrelated file already exists')
    require(revision(path) == expected_revision, 'Profile files changed during apply')
    before = {source: source.read_bytes() if source.exists() else None for source in known | documents.keys()}
    marker_before = marker.read_bytes() if marker.exists() else None
    written = {}
    def current_bytes(source):
        return source.read_bytes() if source.exists() else None
    def write(source, content):
        def unchanged():
            require(current_bytes(source) == before.get(source), f'{source.name}: file changed during save')
        try:
            atomic_write_bytes(source, content, validate=unchanged)
        except MutationIncomplete as error:
            if not error.result.destination_published:
                raise
        written[source] = content
    # Existing ProfileStore recovery copy is fully written before this marker.
    atomic_write_bytes(marker, encode({'recovery': path.with_suffix('.previous.json').name}))
    try:
        for source, data in documents.items():
            if source == path:
                continue
            source.parent.mkdir(parents=True, exist_ok=True)
            content = encode(data)
            if content != before.get(source):
                write(source, content)
        write(path, encode(documents[path]))
        require(load(path, allow_transaction=True) == catalog, 'Catalog changed during save')
        for source in known - documents.keys():
            require(current_bytes(source) == before[source], f'{source.name}: file changed during save')
            source.unlink(missing_ok=True)
            written[source] = None
        marker.unlink()
    except BaseException:
        # Keep the marker if rollback itself fails: never load a mixed catalog.
        for source, published in written.items():
            require(current_bytes(source) == published,
                    f'{source.name}: changed during rollback; recovery marker retained')
            content = before[source]
            if content is None:
                source.unlink(missing_ok=True)
            elif not source.exists() or source.read_bytes() != content:
                atomic_write_bytes(source, content)
        if marker_before is None:
            marker.unlink(missing_ok=True)
        else:
            atomic_write_bytes(marker, marker_before)
        raise
    finally:
        folder = path.parent / (path.stem + '-sections')
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
