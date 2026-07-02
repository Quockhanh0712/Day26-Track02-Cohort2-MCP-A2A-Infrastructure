"""Data governance cho kết nối MCP và A2A."""

try:
    from lab_utils.governance.adk_callbacks import (
        governance_before_agent_callback,
        governance_before_tool_callback,
    )
except ModuleNotFoundError as exc:
    if not str(exc).startswith("No module named 'google"):
        raise

    async def governance_before_agent_callback(*args, **kwargs):
        raise RuntimeError("Cài google-adk để dùng ADK governance callbacks")

    async def governance_before_tool_callback(*args, **kwargs):
        raise RuntimeError("Cài google-adk để dùng ADK governance callbacks")

from lab_utils.governance.audit import AuditLogger
from lab_utils.governance.guard import GovernanceGuard, get_guard
from lab_utils.governance.models import (
    AuditEntry,
    ConnectionType,
    GovernanceDecision,
    GovernanceVerdict,
)
from lab_utils.governance.rate_limit import RateLimiter

__all__ = [
    "AuditEntry",
    "AuditLogger",
    "ConnectionType",
    "GovernanceDecision",
    "GovernanceGuard",
    "GovernanceVerdict",
    "RateLimiter",
    "get_guard",
    "governance_before_agent_callback",
    "governance_before_tool_callback",
]
