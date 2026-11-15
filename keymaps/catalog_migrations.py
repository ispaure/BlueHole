"""Explicit, idempotent migrations. Loading never writes the source catalog."""
from copy import deepcopy
from hashlib import sha256
from .deluxe_schema import assignment_required


def remove_obsolete_dependencies(result):
    for row in result['suppressions'].values():
        row.pop('requires_assignment', None)


def separate_command_owners(result):
    commands = result['commands']
    owners = set()
    bindings = sorted(result['assignments'].items(), key=lambda entry: (
        not assignment_required(result, entry[1]), entry[1]['order']))
    references = [('assignments', id_, row, 'command') for id_, row in bindings]
    references += [('suppressions', id_, row, 'replacement')
                   for id_, row in result['suppressions'].items() if 'replacement' in row]
    for table, id_, row, field in references:
        source = row[field]
        if source in owners:
            suffix = sha256(f'{table}:{id_}'.encode()).hexdigest()[:16]
            target = f'{source[:68]}-binding-{suffix}'
            serial = 0
            while target in commands:
                serial += 1
                target = f'binding-{suffix}-{serial}'
            commands[target] = deepcopy(commands[source])
            row[field] = target
        owners.add(row[field])


MIGRATIONS = (
    ('independent-removal-rules-v1', remove_obsolete_dependencies),
    ('independent-command-settings-v1', separate_command_owners),
)


def migrate_catalog(catalog):
    result = deepcopy(catalog)
    for name, migration in MIGRATIONS:
        migration(result)
    return result
