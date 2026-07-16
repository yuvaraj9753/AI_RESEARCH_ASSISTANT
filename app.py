import streamlit as st

from agents.researcher import do_research
from agents.summarizer import summarize
from agents.chat import follow_up_chat


st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 AI Research Assistant")

st.caption(
    "AI-powered research assistant with web search, source citations, PDF export, and follow-up Q&A."
)

st.markdown("Research → Analyze → Summarize")

# -------------------- Session State --------------------

if "query" not in st.session_state:
    st.session_state.query = ""

if "research" not in st.session_state:
    st.session_state.research = None

if "final" not in st.session_state:
    st.session_state.final = None

if "research_type" not in st.session_state:
    st.session_state.research_type = "General"

if "research_depth" not in st.session_state:
    st.session_state.research_depth = "Standard"

# -------------------- Sidebar --------------------

st.sidebar.header("⚙️ Research Settings")

research_type = st.sidebar.selectbox(
    "Research Type",
    [
        "General",
        "Technical",
        "Academic",
        "Market"
    ],
    index=[
        "General",
        "Technical",
        "Academic",
        "Market"
    ].index(st.session_state.research_type)
)

research_depth = st.sidebar.radio(
    "Research Depth",
    [
        "Quick",
        "Standard",
        "Deep"
    ],
    index=[
        "Quick",
        "Standard",
        "Deep"
    ].index(st.session_state.research_depth)
)

# -------------------- User Input --------------------

query = st.text_input(
    "🔎 Enter your research topic",
    value=st.session_state.query
)

# -------------------- Run Research --------------------

if st.button("🚀 Run Research"):

    if query.strip() == "":
        st.warning("Please enter a research topic.")
        st.stop()

    with st.spinner("🔍 Researching..."):

        research = do_research(
            query=query,
            research_type=research_type,
            research_depth=research_depth
        )

    if "error" in research:
        st.error(research.get("details", research.get("error")))
        st.stop()

    with st.spinner("🧠 Generating Final Report..."):
        final = summarize(query, research)

    if "error" in final:
        st.error(final.get("details", final.get("error")))
        st.stop()

    st.session_state.query = query
    st.session_state.research = research
    st.session_state.final = final
    st.session_state.research_type = research_type
    st.session_state.research_depth = research_depth

# -------------------- Show Report --------------------

if st.session_state.final is not None:

    research = st.session_state.research
    final = st.session_state.final
    query = st.session_state.query

    stats = research.get("statistics", {})

    st.sidebar.header("📊 Research Statistics")

    st.sidebar.metric(
        "Sources Used",
        stats.get("sources_used", 0)
    )

    st.sidebar.metric(
        "Research Type",
        stats.get("research_type", "-")
    )

    st.sidebar.metric(
        "Research Depth",
        stats.get("research_depth", "-")
    )

    st.sidebar.metric(
        "Time Taken",
        f"{stats.get('time_taken', 0)} sec"
    )

    st.sidebar.metric(
        "LLM",
        stats.get("llm_model", "-")
    )

    st.sidebar.metric(
        "Confidence",
        stats.get("confidence", "High")
    )

# -------------------- Report --------------------

    with st.expander("📊 Insights", expanded=True):
        for insight in research.get("insights", []):
            st.write(f"✔️ {insight}")

    with st.expander("🧾 Research Summary"):
        st.write(research.get("summary", ""))

    with st.expander("📖 Introduction"):
        st.write(final.get("introduction", ""))

    with st.expander("🔑 Key Points"):
        for point in final.get("key_points", []):
            st.write(f"👉 {point}")

    with st.expander("✅ Conclusion"):
        st.write(final.get("conclusion", ""))

    # -------------------- Related Topics --------------------

    with st.expander("🧭 Related Topics"):

        related_topics = final.get("related_topics", [])

        if related_topics:
            for topic in related_topics:
                st.write(f"🔹 {topic}")
        else:
            st.write("No related topics found.")

    # -------------------- Sources --------------------

    with st.expander("🔗 Sources"):
        for link in final.get("citations", []):
            st.markdown(f"- {link}")

   

# -------------------- Follow-up Chat --------------------

st.divider()

st.subheader("💬 Follow-up Chat")

question = st.text_input(
    "Ask a follow-up question"
)

if st.button("Ask"):

    if st.session_state.final is None:
        st.warning("⚠️ Please perform research first.")
        st.stop()

    if question.strip() == "":
        st.warning("⚠️ Please enter a question.")
        st.stop()

    with st.spinner("Thinking..."):

        response = follow_up_chat(
            st.session_state.query,
            st.session_state.research,
            st.session_state.final,
            question
        )

    if "error" in response:
        st.error(response["details"])
    else:
        st.success("Answer")
        st.write(response["answer"])