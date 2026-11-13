"""Lossless, hash-checked sharing of repeated native keymap snapshots."""

from collections import Counter
from hashlib import sha256
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def _snapshot(value):
    return isinstance(value, dict) and (
        ('scope' in value and 'items' in value)
        or all(key in value for key in ('target', 'event', 'properties', 'read_issues'))
    )


def pack_native(value):
    """Intern only repeated complete maps/items; preserve every evidence field."""
    counts = Counter()

    def count(node):
        if isinstance(node, dict):
            if _snapshot(node):
                counts[digest(node)] += 1
            for child in node.values():
                count(child)
        elif isinstance(node, list):
            for child in node:
                count(child)

    count(value)
    pool = {}

    def encode(node, inline=False):
        if isinstance(node, dict):
            if not inline and _snapshot(node):
                key = digest(node)
                if counts[key] > 1:
                    if key not in pool:
                        pool[key] = encode(node, inline=True)
                    return {'$snapshot': key}
            return {key: encode(child) for key, child in node.items()}
        if isinstance(node, list):
            return [encode(child) for child in node]
        return node

    encoded = encode(value)
    encoded['snapshot_encoding'] = 'sha256-json-v1'
    encoded['snapshot_pool'] = pool
    encoded['expanded_sha256'] = digest(value)
    return encoded


def unpack_native(value):
    """Resolve local snapshot references, rejecting missing, cyclic or altered data."""
    if 'snapshot_encoding' not in value:
        return value
    if value['snapshot_encoding'] != 'sha256-json-v1':
        raise ValueError('Unknown native evidence snapshot encoding')
    pool, resolved, pending = value['snapshot_pool'], {}, set()

    def decode(node):
        if isinstance(node, dict):
            if set(node) == {'$snapshot'}:
                key = node['$snapshot']
                if key in pending:
                    raise ValueError('Cyclic native evidence snapshot')
                if key not in resolved:
                    pending.add(key)
                    expanded = decode(pool[key])
                    if digest(expanded) != key:
                        raise ValueError('Native evidence snapshot hash mismatch')
                    resolved[key] = expanded
                    pending.remove(key)
                return resolved[key]
            return {key: decode(child) for key, child in node.items()}
        if isinstance(node, list):
            return [decode(child) for child in node]
        return node

    expanded = decode({key: child for key, child in value.items()
                       if key not in ('snapshot_encoding', 'snapshot_pool', 'expanded_sha256')})
    if set(resolved) != set(pool):
        raise ValueError('Unreferenced native evidence snapshot')
    if digest(expanded) != value['expanded_sha256']:
        raise ValueError('Expanded native evidence hash mismatch')
    return expanded
