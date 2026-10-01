import json
import time

from langchain_core.messages import HumanMessage

from langgraph.prebuilt import ToolNode

from services.groq_service import get_llm
from services.search_service import web_search
from utils.helpers import safe_json_parse

from prompts.planner_prompt import PLANNER_PROMPT
from prompts.analysis_prompt import ANALYSIS_PROMPT
from prompts.evaluation_prompt import EVALUATION_PROMPT
from prompts.summary_prompt import SUMMARY_PROMPT


# =========================================================
# TOOL NODE
# =========================================================

search_tool_node = ToolNode(
    [web_search]
)


# =========================================================
# PLANNER NODE
# =========================================================

def planner_node(state):

    llm = get_llm()

    query = state["query"]
    research_type = state["research_type"]
    research_depth = state["research_depth"]

    prompt = PLANNER_PROMPT.format(
        query=query,
        research_type=research_type,
        research_depth=research_depth
    )

    try:

        response = llm.invoke(prompt)

        plan = safe_json_parse(
            response.content
        )

        if "error" in plan:

            return {
                "error": plan.get(
                    "error",
                    "Planning failed."
                )
            }

        return {
            "research_plan": plan,
            "search_queries": plan.get(
                "search_queries",
                []
            )
        }

    except Exception as e:

        return {
            "error": f"Planner failed: {str(e)}"
        }


# =========================================================
# HUMAN APPROVAL NODE
# =========================================================

def human_approval_node(state):

    from langgraph.types import interrupt

    plan = state.get(
        "research_plan",
        {}
    )

    feedback = interrupt({
        "type": "research_plan_approval",
        "message": "Please review the research plan.",
        "plan": plan
    })

    if not isinstance(feedback, dict):

        return {
            "plan_approved": True,
            "human_feedback": ""
        }

    approved = feedback.get(
        "approved",
        False
    )

    modified_plan = feedback.get(
        "plan"
    )

    if modified_plan:

        return {
            "plan_approved": approved,
            "human_feedback": feedback.get(
                "feedback",
                ""
            ),
            "research_plan": modified_plan,
            "search_queries": modified_plan.get(
                "search_queries",
                []
            )
        }

    return {
        "plan_approved": approved,
        "human_feedback": feedback.get(
            "feedback",
            ""
        )
    }


# =========================================================
# SEARCH AGENT NODE
# =========================================================

def search_agent_node(state):

    llm = get_llm()

    search_queries = state.get(
        "search_queries",
        []
    )

    if not search_queries:

        search_queries = [
            state["query"]
        ]

    query_text = "\n".join(
        [
            f"{index + 1}. {query}"
            for index, query in enumerate(
                search_queries
            )
        ]
    )

    prompt = f"""
You are the web research tool-calling agent.

Research topic:
{state["query"]}

Research type:
{state["research_type"]}

The research planner created these search queries:

{query_text}

Use the web_search tool to collect current information.

You should perform web searches for the important queries.

Do not answer the research question directly.
Use the web_search tool.
"""

    llm_with_tools = llm.bind_tools(
        [web_search]
    )

    try:

        response = llm_with_tools.invoke(
            prompt
        )

        return {
            "messages": [response]
        }

    except Exception as e:

        return {
            "error": f"Search agent failed: {str(e)}"
        }


# =========================================================
# ANALYZE NODE
# =========================================================

def analyze_node(state):

    llm = get_llm()

    messages = state.get(
        "messages",
        []
    )

    tool_results = []

    for message in messages:

        if getattr(
            message,
            "type",
            None
        ) == "tool":

            try:

                content = message.content

                parsed = json.loads(
                    content
                )

                tool_results.append(
                    parsed
                )

            except Exception:

                tool_results.append({
                    "raw_content": message.content
                })

    if not tool_results:

        return {
            "error": "No web search results were returned."
        }

    formatted_results = json.dumps(
        tool_results,
        indent=2,
        ensure_ascii=False
    )

    prompt = ANALYSIS_PROMPT.format(
        query=state["query"],
        research_type=state["research_type"],
        research_plan=json.dumps(
            state.get(
                "research_plan",
                {}
            ),
            indent=2
        ),
        search_results=formatted_results
    )

    try:

        response = llm.invoke(
            prompt
        )

        analysis = safe_json_parse(
            response.content
        )

        if "error" in analysis:

            return {
                "error": "Research analysis failed."
            }

        all_sources = []

        for result in tool_results:

            all_sources.extend(
                result.get(
                    "sources",
                    []
                )
            )

        unique_sources = list(
            dict.fromkeys(
                all_sources
            )
        )

        return {
            "analysis": analysis,
            "insights": analysis.get(
                "insights",
                []
            ),
            "sources": unique_sources
        }

    except Exception as e:

        return {
            "error": f"Analysis failed: {str(e)}"
        }


# =========================================================
# EVALUATION NODE
# =========================================================

def evaluation_node(state):

    llm = get_llm()

    iteration = state.get(
        "research_iterations",
        0
    )

    analysis = state.get(
        "analysis",
        {}
    )

    sources = state.get(
        "sources",
        []
    )

    prompt = EVALUATION_PROMPT.format(
        query=state["query"],
        research_type=state["research_type"],
        research_plan=json.dumps(
            state.get(
                "research_plan",
                {}
            ),
            indent=2
        ),
        analysis=json.dumps(
            analysis,
            indent=2,
            ensure_ascii=False
        ),
        sources="\n".join(sources),
        iteration=iteration
    )

    try:

        response = llm.invoke(
            prompt
        )

        evaluation = safe_json_parse(
            response.content
        )

        if "error" in evaluation:

            return {
                "enough_information": True,
                "evaluation_reason": (
                    "Evaluation failed; "
                    "proceeding with current research."
                )
            }

        enough_information = bool(
            evaluation.get(
                "enough_information",
                False
            )
        )

        # Safety limit to avoid infinite loops.
        if iteration >= 2:

            enough_information = True

        return {
            "enough_information": enough_information,
            "evaluation_reason": evaluation.get(
                "reason",
                ""
            ),
            "research_iterations": iteration + 1
        }

    except Exception as e:

        return {
            "enough_information": True,
            "evaluation_reason": (
                f"Evaluation error: {str(e)}"
            ),
            "research_iterations": iteration + 1
        }


# =========================================================
# PREPARE NEXT SEARCH
# =========================================================

def prepare_next_search_node(state):

    analysis = state.get(
        "analysis",
        {}
    )

    unanswered = analysis.get(
        "unanswered_questions",
        []
    )

    if not unanswered:

        unanswered = [
            state["query"]
        ]

    return {
        "search_queries": unanswered[:5]
    }


# =========================================================
# SUMMARY NODE
# =========================================================

def summary_node(state):

    llm = get_llm()

    analysis = state.get(
        "analysis",
        {}
    )

    insights = analysis.get(
        "insights",
        []
    )

    sources = state.get(
        "sources",
        []
    )

    prompt = SUMMARY_PROMPT.format(
        query=state["query"],
        insights=json.dumps(
            insights,
            ensure_ascii=False
        ),
        sources="\n".join(
            sources
        )
    )

    try:

        response = llm.invoke(
            prompt
        )

        final_report = safe_json_parse(
            response.content
        )

        if "error" in final_report:

            return {
                "error": "Final report generation failed."
            }

        final_report["citations"] = sources

        return {
            "final_report": final_report
        }

    except Exception as e:

        return {
            "error": (
                f"Summary generation failed: {str(e)}"
            )
        }


# =========================================================
# STATISTICS NODE
# =========================================================

def statistics_node(state):

    start_time = state.get(
        "start_time",
        time.time()
    )

    elapsed = round(
        time.time() - start_time,
        2
    )

    statistics = {
        "research_type": state.get(
            "research_type",
            "-"
        ),
        "research_depth": state.get(
            "research_depth",
            "-"
        ),
        "sources_used": len(
            state.get(
                "sources",
                []
            )
        ),
        "research_iterations": state.get(
            "research_iterations",
            0
        ),
        "time_taken": elapsed,
        "llm_model": "openai/gpt-oss-20b"
    }

    return {
        "statistics": statistics
    }


# =========================================================
# ROUTER
# =========================================================

def route_after_evaluation(state):

    if state.get(
        "enough_information",
        False
    ):

        return "summary"

    return "search_again"