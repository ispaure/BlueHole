"""Compatibility import for the shared Perforce implementation."""
import sys
from ...Lib.commonUtils.wrappers.perforce import p4_file_status as _shared
sys.modules[__name__] = _shared
