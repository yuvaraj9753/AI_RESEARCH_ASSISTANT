import json


def safe_json_parse(text: str) -> dict:
    """
    Safely parses JSON returned by the LLM.
    If the response contains extra text before or after the JSON,
    it attempts to extract only the JSON object.
    """

    try:
        return json.loads(text)

    except json.JSONDecodeError:

        try:
            start = text.find("{")
            end = text.rfind("}") + 1

            if start == -1 or end == 0:
                raise ValueError("No JSON object found.")

            return json.loads(text[start:end])

        except Exception:

            return {
                "error": "Invalid JSON",
                "raw": text
            }