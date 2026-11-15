"""Dependency changes between immutable catalog snapshots, without Blender."""
from dataclasses import dataclass
from .catalog_plan import profile_assignment_id
from .deluxe_schema import same_value

TABLES = ('categories', 'sections', 'commands', 'events', 'assignments', 'suppressions')


@dataclass(frozen=True)
class CatalogChanges:
    rows: dict
    assignments: frozenset
    suppressions: frozenset

    @classmethod
    def between(cls, before, after):
        rows = {table: frozenset(key for key in before[table].keys() | after[table].keys()
                                if not same_value(before[table].get(key), after[table].get(key)))
                for table in TABLES}
        assignments, suppressions, features, chains = set(), set(), set(), set()
        for catalog in (before, after):
            sections = rows['sections'] | {key for key, row in catalog['sections'].items()
                                           if row['category'] in rows['categories']}
            for key, row in catalog['assignments'].items():
                if (key in rows['assignments'] or row['command'] in rows['commands']
                        or row['event'] in rows['events'] or row['section'] in sections):
                    assignments.add(key)
                    features.add(row['feature'])
                    if row.get('dispatch_group'):
                        chains.add(row['dispatch_group'])
            suppressions.update(key for key, row in catalog['suppressions'].items()
                                if key in rows['suppressions'] or row['section'] in sections
                                or row.get('replacement') in rows['commands'])
        # A feature is atomic; a dispatch review applies to every member. Editing
        # one member can revoke the review for otherwise unchanged features.
        for catalog in (before, after):
            features.update(row['feature'] for row in catalog['assignments'].values()
                            if row.get('dispatch_group') in chains)
        for catalog in (before, after):
            assignments.update(key for key, row in catalog['assignments'].items()
                               if row['feature'] in features)
        return cls(rows, frozenset(assignments), frozenset(suppressions))

    def replan(self, resolver, preferences, before, after, previous_plan):
        """Recompile complete affected features, retaining source order globally."""
        if not self.assignments and not self.rows['sections'] and not self.rows['categories']:
            return previous_plan
        _, groups = previous_plan
        groups = {owner: requests for owner, requests in groups.items()
                  if not any(profile_assignment_id(r.request_id) in self.assignments for r in requests)}
        sections, changed = resolver.plan(after, preferences,
            assignment_ids=self.assignments & after['assignments'].keys())
        groups.update(changed)
        groups = dict(sorted(groups.items(), key=lambda entry: min(
            after['assignments'][profile_assignment_id(r.request_id)]['order'] for r in entry[1])))
        return sections, groups
