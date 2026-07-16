from services.groq_service import get_llm
from prompts.summary_prompt import SUMMARY_PROMPT
from utils.helpers import safe_json_parse


def summarize(query: str, research: dict):

    llm = get_llm()

    prompt = SUMMARY_PROMPT.format(
        query=query,
        insights=research.get("insights", [])
    )

    try:

        response = llm.invoke(prompt)

        data = safe_json_parse(response.content)

        data["citations"] = research.get("citations", [])

        if "related_topics" not in data:
            data["related_topics"] = []

        return data

    except Exception as e:

        return {
            "error": "Summarization failed",
            "details": str(e)
        }