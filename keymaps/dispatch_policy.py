"""Reviewed shared events are capabilities tied to semantics, never just labels."""
from collections import defaultdict
from functools import lru_cache
import json
from pathlib import Path

from .catalog_inventory import assignment_semantics, digest


@lru_cache(maxsize=1)
def manifest():
    return json.loads(Path(__file__).with_name('dispatch-chains.json').read_text(encoding='utf-8'))['chains']


def reviewed_groups(catalog, reviews=None):
    reviews = manifest() if reviews is None else reviews
    groups = defaultdict(list)
    for id_, row in sorted(catalog['assignments'].items(), key=lambda item: item[1]['order']):
        if row.get('dispatch_group'):
            groups[row['dispatch_group']].append(id_)
    accepted = set()
    for group, ids in groups.items():
        review = reviews.get(group)
        if not review:
            continue
        expected = {row['id']: row['signature'] for row in review['members']}
        if ids != [id_ for id_ in expected if id_ in ids]:
            continue
        for id_ in ids:
            semantics = assignment_semantics(catalog, id_)
            semantics.pop('order')
            if digest(semantics) != expected[id_]:
                break
        else:
            accepted.add(group)
    return frozenset(accepted)


def reviewed_chain(catalog, ids, groups):
    group = catalog['assignments'][ids[0]].get('dispatch_group')
    return group in groups and all(catalog['assignments'][id_].get('dispatch_group') == group for id_ in ids)
