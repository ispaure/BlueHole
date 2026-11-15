"""Conservative event overlap hints, not proof of operator dispatch conflicts."""
from collections import defaultdict
from itertools import combinations


def events_overlap(left, right):
    if left.type != right.type or left.map_type != right.map_type:
        return False
    if left.value != right.value and 'ANY' not in (left.value, right.value):
        return False
    if left.direction != right.direction and 'ANY' not in (left.direction, right.direction):
        return False
    if left.key_modifier != right.key_modifier:
        return False
    # repeat=True also accepts the initial key press. Modifier -1 and `any`
    # match either state. hyper=None means the host has no Hyper capability.
    for name in ('shift', 'ctrl', 'alt', 'oskey', 'hyper'):
        a, b = getattr(left, name), getattr(right, name)
        if not (left.any or right.any or a in (-1, None) or b in (-1, None) or a == b):
            return False
    return True


def potential_overlaps(active):
    """Index by context/key first; compare only non-identical event patterns."""
    buckets = defaultdict(list)
    for (scope, event), ids in active.items():
        buckets[scope, event.type, event.map_type].append((event, ids))
    return tuple(tuple(left_ids + right_ids) for bucket in buckets.values()
                 for (left, left_ids), (right, right_ids) in combinations(bucket, 2)
                 if events_overlap(left, right))
