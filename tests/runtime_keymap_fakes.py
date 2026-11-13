"""Small Blender keymap double with the measured 4.5 forward-prepend merge.

The objects deliberately have identity and lifetime.  A removed RNA-like item
cannot be used as a handle to a newly created item with identical fields.
"""

from __future__ import annotations

from copy import deepcopy
from itertools import count
from types import SimpleNamespace


_pointers = count(1000)
_item_ids = count(1)
EVENT_DEFAULTS = dict(type='A', value='PRESS', any=False, shift=False,
                      ctrl=False, alt=False, oskey=False, hyper=False,
                      key_modifier='NONE', direction='ANY', repeat=False,
                      map_type='KEYBOARD')


class FakeItem:
    _readable = frozenset({'_alive', '_pointer', '__class__', '__dict__',
                           '__getattribute__', 'as_pointer', 'invalidate', 'clone'})

    def __init__(self, idname='', *, prop_values=None, prop_schema=None,
                 prop_fail=None, active=True, modal_value='', **event):
        self._alive = True
        self._pointer = next(_pointers)
        self.id = next(_item_ids)
        self.idname = idname
        self.prop_schema = prop_schema
        self.properties = FakeProperties(prop_values or {}, prop_schema, prop_fail)
        self.active = active
        self.propvalue = modal_value
        self.is_user_defined = False
        self.is_user_modified = False
        for name, default in EVENT_DEFAULTS.items():
            setattr(self, name, event.get(name, default))

    def __getattribute__(self, name):
        if not name.startswith('_') and name not in FakeItem._readable:
            if not object.__getattribute__(self, '_alive'):
                raise ReferenceError('removed keymap item')
        return object.__getattribute__(self, name)

    def as_pointer(self):
        if not self._alive:
            raise ReferenceError('removed keymap item')
        return self._pointer

    def invalidate(self):
        self._alive = False

    def clone(self):
        copy = FakeItem(self.idname, prop_values=dict(self.properties),
                        prop_schema=self.prop_schema, active=self.active,
                        modal_value=self.propvalue,
                        **{name: getattr(self, name, default)
                           for name, default in EVENT_DEFAULTS.items()})
        for name in EVENT_DEFAULTS:
            if name not in self.__dict__:
                delattr(copy, name)
        return copy

    def alias(self):
        """Another live Python wrapper for the same native item identity."""
        copy = self.clone()
        copy._pointer = self._pointer
        copy.id = self.id
        return copy


class ReusedIdWrapper:
    """Retained RNA-like wrapper whose ID follows live memory at its address."""
    def __init__(self, map_, item):
        self.map = map_
        self.pointer = item.as_pointer()

    def as_pointer(self):
        return self.pointer

    @property
    def id(self):
        return next((item.id for item in self.map.keymap_items
                     if item.as_pointer() == self.pointer), None)


class FakeProperties(dict):
    def __init__(self, values, schema=None, fail=None):
        super().__init__({**(schema or {}), **values})
        self._fail = fail
        self.bl_rna = SimpleNamespace(properties=[SimpleNamespace(identifier=name,
                             type='BOOLEAN' if isinstance(value, bool) else 'INT',
                             is_array=False) for name, value in
                             (schema or values).items()])

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name.startswith('_') or name == 'bl_rna':
            return object.__setattr__(self, name, value)
        if self._fail == name:
            raise RuntimeError('injected property setter failure')
        self[name] = value


class FakeItems:
    def __init__(self, map_):
        self.map = map_
        self.rows = []
        self.created = 0
        self.removed = 0
        self.fail_after_create = False
        self.fail_next_new = False
        self.fail_create_at = None
        self.new_prop_fail = None
        self.new_prop_schema = None
        self.new_missing_fields = set()
        self.fail_next_remove = False
        self.remove_failures_remaining = 0
        self.return_alias_wrappers = False

    def __iter__(self):
        return iter(tuple(self.rows))

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def append_fixture(self, item):
        self.rows.append(item)
        return item

    def new(self, idname, type, value, *, head=False, **event):
        if self.fail_next_new or self.fail_create_at == self.created + 1:
            self.fail_next_new = False
            self.fail_create_at = None
            raise RuntimeError('injected creation failure')
        event.setdefault('map_type', 'MOUSE' if 'MOUSE' in type or 'TRACKPAD' in type
                         else 'NDOF' if type.startswith('NDOF') else 'KEYBOARD')
        item = FakeItem(idname, type=type, value=value,
                        prop_schema=self.new_prop_schema,
                        prop_fail=self.new_prop_fail, **event)
        for field in self.new_missing_fields:
            delattr(item, field)
        self.rows.insert(0 if head else len(self.rows), item)
        self.created += 1
        if self.fail_after_create:
            self.fail_after_create = False
            raise RuntimeError('injected failure after native creation')
        return item.alias() if self.return_alias_wrappers else item

    def new_from_item(self, item, *, head=False):
        copy = item.clone()
        self.rows.insert(0 if head else len(self.rows), copy)
        self.created += 1
        return copy

    def remove(self, item):
        if self.fail_next_remove or self.remove_failures_remaining:
            self.fail_next_remove = False
            if self.remove_failures_remaining:
                self.remove_failures_remaining -= 1
            raise RuntimeError('injected native remove failure')
        for index, row in enumerate(self.rows):
            if (row is item or (self.return_alias_wrappers and row._pointer == item._pointer
                               and row.id == item.id)):
                self.rows.pop(index)
                row.invalidate()
                if row is item:
                    item.invalidate()
                self.removed += 1
                return
        raise ReferenceError('item is no longer a member of this map')


class FakeMap:
    def __init__(self, name, space_type='EMPTY', region_type='WINDOW',
                 is_modal=False, is_tool=None):
        self._pointer = next(_pointers)
        self.name = name
        self.space_type = space_type
        self.region_type = region_type
        self.is_modal = is_modal
        self.is_tool = is_tool
        self.keymap_items = FakeItems(self)

    def as_pointer(self):
        return self._pointer


class FakeMaps:
    def __init__(self):
        self.rows = []

    def __iter__(self):
        return iter(tuple(self.rows))

    def get(self, name):
        return next((row for row in self.rows if row.name == name), None)

    def new(self, name, space_type='EMPTY', region_type='WINDOW',
            modal=False, tool=None):
        row = FakeMap(name, space_type, region_type, modal, tool)
        self.rows.append(row)
        return row

    def remove(self, row):
        self.rows.remove(row)
        for item in row.keymap_items:
            item.invalidate()


class FakeConfig:
    def __init__(self, name):
        self.name = name
        self.keymaps = FakeMaps()


class FakeConfigs(SimpleNamespace):
    def __init__(self, **roles):
        super().__init__(**roles)
        self.update_calls = []

    def update(self):
        self.update_calls.append(tuple(
            (map_.name, tuple(item.idname for item in map_.keymap_items))
            for map_ in self.addon.keymaps))


class MergedMaps:
    """Read-only snapshot: add-on source items are prepended in source order."""
    def __init__(self, configs):
        self.configs = configs

    def __iter__(self):
        base = self.configs.default
        addon = self.configs.addon
        keys = []
        for config in (base, addon):
            if config is not None:
                for map_ in config.keymaps:
                    key = (map_.name, map_.space_type, map_.region_type,
                           map_.is_modal, getattr(map_, 'is_tool', None))
                    if key not in keys:
                        keys.append(key)
        for key in keys:
            merged = FakeMap(*key)
            if base is not None:
                for map_ in base.keymaps:
                    if (map_.name, map_.space_type, map_.region_type,
                            map_.is_modal, getattr(map_, 'is_tool', None)) == key:
                        merged.keymap_items.rows.extend(row.clone() for row in map_.keymap_items)
            if addon is not None:
                for map_ in addon.keymaps:
                    if (map_.name, map_.space_type, map_.region_type,
                            map_.is_modal, getattr(map_, 'is_tool', None)) == key:
                        for row in map_.keymap_items:
                            merged.keymap_items.rows.insert(0, row.clone())
            yield merged

    def get(self, name):
        return next((map_ for map_ in self if map_.name == name), None)


class FakeRuntime:
    def __init__(self):
        self.configs = FakeConfigs(default=FakeConfig('default'),
                                   addon=FakeConfig('addon'), active=None,
                                   user=None)
        self.configs.active = self.configs.default
        self.configs.user = SimpleNamespace(name='user', keymaps=MergedMaps(self.configs))
        self.bpy = SimpleNamespace(context=SimpleNamespace(
            window_manager=SimpleNamespace(keyconfigs=self.configs)))

    def map(self, role, name='3D View', *, space='VIEW_3D', modal=False,
            tool=None):
        return getattr(self.configs, role).keymaps.new(
            name, space_type=space, region_type='WINDOW', modal=modal,
            tool=tool)

    def replace_config(self, role):
        old = getattr(self.configs, role)
        for map_ in old.keymaps:
            old.keymaps.remove(map_)
        new = FakeConfig(role + '-replacement')
        setattr(self.configs, role, new)
        if role == 'default':
            self.configs.active = new
        return new


def row(idname='object.select_all', *, key='A', prop_values=None,
        active=True, modal_value='', **event):
    return FakeItem(idname, prop_values=deepcopy(prop_values), active=active,
                    modal_value=modal_value, type=key, **event)
