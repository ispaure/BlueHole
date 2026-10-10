"""Supply BlueHole preferences lazily to the shared Perforce models."""
from ...Lib.commonUtils.integrations.wrappers.perforce import PerforceRuntime, configure_runtime
from ...Lib.commonUtils.runtime.platform import OS, get_os


def _executable(platform):
    if platform is OS.WIN:
        return 'p4'
    from ...preferences.prefs import prefs
    settings = prefs().sourcecontrol
    if platform is OS.MAC:
        return f'{settings.p4v_app_path_mac}/Contents/Resources/p4_parallel'
    return settings.p4_parallel_path_linux


def _environment():
    from ...preferences.prefs import prefs
    settings = prefs().sourcecontrol
    if not settings.source_control_enable or settings.source_control_solution != 'perforce':
        return {}
    platform = get_os()
    if platform is OS.WIN and not settings.win32_env_override:
        return {}
    prefix = 'linux' if platform is OS.LINUX else 'macos'
    return {key: getattr(settings, f'{prefix}_env_setting_{key.lower()}')
            for key in ('P4USER', 'P4PORT', 'P4CLIENT')}


def _binary_template():
    from ...blenderUtils import blenderFile
    return blenderFile.get_blue_hole_lib_path() / 'binary_template.bin'


configure_runtime(PerforceRuntime(_executable, _environment, _binary_template))
