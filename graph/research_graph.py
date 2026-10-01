import time

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from langgraph.checkpoint.memory import InMemorySaver

from graph.state import ResearchState

from graph.nodes import (
    planner_node,
    human_approval_node,
    search_agent_node,
    search_tool_node,
    analyze_node,
    evaluation_node,
    prepare_next_search_node,
    summary_node,
    statistics_node,
    route_after_evaluation
)


# =========================================================
# CHECKPOINTER
# =========================================================

checkpointer = InMemorySaver()


# =========================================================
# GRAPH BUILDER
# =========================================================

def build_research_graph():

    builder = StateGraph(
        ResearchState
    )

    # -------------------------
    # Nodes
    # -------------------------

    builder.add_node(
        "planner",
        planner_node
    )

    builder.add_node(
        "human_approval",
        human_approval_node
    )

    builder.add_node(
        "search_agent",
        search_agent_node
    )

    builder.add_node(
        "search_tools",
        search_tool_node
    )

    builder.add_node(
        "analyze",
        analyze_node
    )

    builder.add_node(
        "evaluate",
        evaluation_node
    )

    builder.add_node(
        "prepare_next_search",
        prepare_next_search_node
    )

    builder.add_node(
        "summary",
        summary_node
    )

    builder.add_node(
        "statistics",
        statistics_node
    )

    # -------------------------
    # Edges
    # -------------------------

    builder.add_edge(
        START,
        "planner"
    )

    builder.add_edge(
        "planner",
        "human_approval"
    )

    builder.add_edge(
        "human_approval",
        "search_agent"
    )

    # Tool-calling workflow
    builder.add_edge(
        "search_agent",
        "search_tools"
    )

    builder.add_edge(
        "search_tools",
        "analyze"
    )

    builder.add_edge(
        "analyze",
        "evaluate"
    )

    # Conditional edge
    builder.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "summary": "summary",
            "search_again": "prepare_next_search"
        }
    )

    builder.add_edge(
        "prepare_next_search",
        "search_agent"
    )

    builder.add_edge(
        "summary",
        "statistics"
    )

    builder.add_edge(
        "statistics",
        END
    )

    return builder.compile(
        checkpointer=checkpointer
    )


research_graph = build_research_graph()