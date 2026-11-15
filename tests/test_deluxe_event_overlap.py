"""Overlap hints model input matching without granting dispatch exemptions."""
from dataclasses import replace
import importlib
import unittest
import test_deluxe_profiles


class OverlapTests(unittest.TestCase):
    def setUp(self):
        self.h = test_deluxe_profiles.ProfileTests()
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)
        self.api = importlib.import_module('_deluxe_profiles_test.keymaps.event_overlap')
        self.event = self.h.core.KeymapEvent('Q')

    def test_wildcards_modifiers_repeat_and_direction(self):
        event = self.event
        overlap = self.api.events_overlap
        for other in (replace(event, any=True), replace(event, shift=-1),
                      replace(event, value='ANY'), replace(event, repeat=True)):
            self.assertTrue(overlap(event, other))
            self.assertTrue(overlap(other, event))
        for other in (replace(event, shift=True), replace(event, type='W'),
                      replace(event, value='RELEASE'), replace(event, key_modifier='D')):
            self.assertFalse(overlap(event, other))
        self.assertFalse(overlap(replace(event, direction='NORTH'), replace(event, direction='SOUTH')))

    def test_potential_overlap_respects_context_and_excludes_exact_groups(self):
        scope = self.h.core.KeymapScope('3D View')
        active = {(scope, self.event): ['a', 'b'], (scope, replace(self.event, any=True)): ['c'],
                  (replace(scope, name='Image'), self.event): ['d']}
        self.assertEqual(self.api.potential_overlaps(active), (('a', 'b', 'c'),))
