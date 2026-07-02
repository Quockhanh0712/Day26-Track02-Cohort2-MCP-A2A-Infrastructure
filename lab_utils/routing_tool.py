"""Semantic routing tool — gợi ý specialist cho orchestrator (capstone)."""

from __future__ import annotations

from lab_utils.semantic_router import AgentCapability, SemanticRouter

_DEFAULT_AGENTS = [
    AgentCapability(
        name="search_agent",
        description="Tìm kiếm web tài liệu nghiên cứu bằng chứng bài viết nguồn MCP A2A",
        tags=["search", "web", "documents", "tim", "kiem", "bai", "viet", "nguon"],
    ),
    AgentCapability(
        name="database_agent",
        description="SQL metrics phân tích database truy vấn SELECT agent_metrics độ trễ trung bình",
        tags=["sql", "metrics", "database", "select", "agent_metrics", "latency", "do", "tre", "trung", "binh"],
    ),
    AgentCapability(
        name="synthesis_agent",
        description="Tóm tắt kết hợp kết quả thành báo cáo cuối executive tổng hợp",
        tags=["summary", "report", "synthesis", "tom", "tat", "bao", "cao", "tong", "hop"],
    ),
]

_router = SemanticRouter(agents=_DEFAULT_AGENTS)


def suggest_routing(user_request: str) -> dict:
    """Gợi ý specialist phù hợp cho yêu cầu người dùng (chỉ mang tính tư vấn).

    Orchestrator vẫn quyết định cuối cùng; tool này dùng semantic router
    bag-of-words để xếp hạng search_agent, database_agent, synthesis_agent.

    Args:
        user_request: Câu hỏi hoặc nhiệm vụ nghiên cứu từ người dùng.

    Returns:
        Dict với recommended_agent, top_candidates (name + score), fallback.
    """
    candidates = _router.route(user_request, top_k=3)
    recommended = _router.route_with_fallback(user_request, fallback="orchestrator")
    return {
        "recommended_agent": recommended,
        "top_candidates": [
            {"agent": name, "score": round(score, 3)} for name, score in candidates
        ],
        "fallback": "orchestrator",
        "note": "Gợi ý mang tính tư vấn — orchestrator quyết định MCP vs A2A.",
    }
