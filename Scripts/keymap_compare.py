"""Compare captured keymap semantics, retaining duplicates and registration order.

python Scripts/keymap_compare.py before.json after.json --role user --output delta.json
Native IDs, saved-modification flags, and capture timestamps are not semantics.
Read issues are retained: an unreadable value must never become an exact match.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def rows(snapshot, role):
    result = []
    for map_ in snapshot['roles'][role]['maps']:
        for item in map_['items']:
            result.append({'scope': map_['scope'], **{key: item[key] for key in
                ('target', 'event', 'properties', 'active', 'read_issues')}})
    return result


def compare(before, after, role='user'):
    encode = lambda row: json.dumps(row, sort_keys=True, separators=(',', ':'))
    left, right = ([encode(row) for row in rows(snapshot, role)] for snapshot in (before, after))
    a, b = Counter(left), Counter(right)
    expand = lambda counts: [{'count': count, 'binding': json.loads(row)} for row, count in sorted(counts.items())]
    return {'comparison_version': 1, 'role': role, 'ordered_equal': left == right,
            'multiset_equal': a == b, 'before_count': len(left), 'after_count': len(right),
            'removed': expand(a - b), 'added': expand(b - a)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('--role', choices=('default', 'addon', 'user', 'active'), default='user')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = compare(json.loads(args.before.read_text()), json.loads(args.after.read_text()), args.role)
    report['input_sha256'] = {name: hashlib.sha256(getattr(args, name).read_bytes()).hexdigest() for name in ('before', 'after')}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
