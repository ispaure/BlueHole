"""Compatibility import for the shared Perforce implementation."""
import sys
from ...Lib.commonUtils.integrations.wrappers.perforce import p4_file_group as _shared
sys.modules[__name__] = _shared
