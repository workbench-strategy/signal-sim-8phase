"""
Shared ITS lab platform.

Domain-agnostic seams used by signals, VMS, RWIS, CCTV, and future adapters.
See docs/ARCHITECTURE.md and docs/ITS_LAB_STRATEGY.md.
"""

from its.adapters import DomainAdapter, DomainHealth, DomainStatus
from its.events import Recommendation
from its.policies.base import Observation, Policy
from its.profile import DeviceProfile, load_device_profile
from its.registry import AdapterRegistry
from its.shadow import ShadowBus

__all__ = [
    "AdapterRegistry",
    "DeviceProfile",
    "DomainAdapter",
    "DomainHealth",
    "DomainStatus",
    "Observation",
    "Policy",
    "Recommendation",
    "ShadowBus",
    "load_device_profile",
]

__version__ = "0.1.0"
