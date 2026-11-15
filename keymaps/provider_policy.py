"""Provider identity and generic-operator dependencies, separate from UI labels.

Ordinary provider operators prove availability through RNA. Generic Blender
operators need an additional dependency only when their target outlives the
provider. Menu/panel classes are checked separately by their registered class.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderPolicy:
    label: str
    modules: tuple[str, ...]
    generic_operators: tuple[str, ...] = ()
    replacement_versions: tuple[tuple[int, ...], ...] = ()


PROVIDERS = {
    'Zen UV': ProviderPolicy('Zen UV', ('ZenUV',), ('wm.',)),
    'MACHIN3tools': ProviderPolicy('MACHIN3tools', ('MACHIN3tools',), replacement_versions=((1, 13, 2),)),
}


def command_addon(command):
    provider = PROVIDERS.get(command.get('provider'))
    if provider and command.get('operator', '').startswith(provider.generic_operators):
        return provider.modules[0]
    return ''


def module_matches(module, aliases):
    return any(module == alias or module.startswith('bl_ext.') and module.endswith('.' + alias) for alias in aliases)


def required_class(command):
    if command.get('operator') in {'wm.call_menu', 'wm.call_menu_pie', 'wm.call_panel'}:
        return command.get('properties', {}).get('name', '')
    return ''
