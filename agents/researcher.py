import time

from services.groq_service import get_llm
from services.search_service import search_web
from prompts.research_prompt import RESEARCH_PROMPT
from utils.helpers import safe_json_parse


def do_research(
    query: str,
    research_type: str = "General",
    research_depth: str = "Standard"
):

    llm = get_llm()

    # -------------------------
    # Research Depth
    # -------------------------

    depth_map = {
        "Quick": 3,
        "Standard": 5,
        "Deep": 10
    }

    max_results = depth_map.get(research_depth, 5)

    start_time = time.time()

    search_data = search_web(
        query=query,
        max_results=max_results
    )

    if "error" in search_data:
        return search_data

    prompt = RESEARCH_PROMPT.format(
        query=query,
        search_results=search_data["raw_results"],
        research_type=research_type
    )

    try:

        response = llm.invoke(prompt)

        data = safe_json_parse(response.content)

        end_time = time.time()

        # -------------------------
        # Extra Statistics
        # -------------------------

        data["citations"] = search_data["sources"]

        data["statistics"] = {
            "research_type": research_type,
            "research_depth": research_depth,
            "sources_used": len(search_data["sources"]),
            "time_taken": round(end_time - start_time, 2),
            "llm_model": "Llama-3.3-70B",
            "confidence": "High"
        }

        return data

    except Exception as e:

        return {
            "error": "Research failed",
            "details": str(e)
        }