SUMMARY_PROMPT = """
You are an expert AI Research Assistant.

Using the research insights below, generate a professional final report.

Topic:
{query}

Research Insights:
{insights}

Instructions:

1. Write a concise introduction.
2. Extract the most important key points.
3. Write a meaningful conclusion.
4. Suggest 5 related research topics that users may want to explore next.

Return ONLY valid JSON.

{{
    "introduction": "",
    "key_points": [
        "Point 1",
        "Point 2"
    ],
    "conclusion": "",
    "related_topics": [
        "Topic 1",
        "Topic 2",
        "Topic 3",
        "Topic 4",
        "Topic 5"
    ]
}}
"""