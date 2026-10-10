"""Compatibility import for the shared Perforce implementation."""
import sys
from ...Lib.commonUtils.wrappers.perforce import p4_info as _shared
sys.modules[__name__] = _shared
