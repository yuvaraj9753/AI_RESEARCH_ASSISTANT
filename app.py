import uuid

import streamlit as st

from langchain_core.messages import HumanMessage
from langgraph.types import Command

from agents.chat import follow_up_chat
from graph.research_graph import research_graph

from utils.pdf_export import create_research_pdf


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide"
)


st.title("🔬 AI Research Assistant")

st.caption(
    "Agentic AI research assistant with LangGraph, "
    "web search, human approval, source citations, "
    "iterative research, PDF export and follow-up Q&A."
)

st.markdown(
    "Research Planning → Human Approval → "
    "Web Search → Analysis → Evaluation → Report"
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {

    "query": "",

    "research_type": "General",

    "research_depth": "Standard",

    "research_plan": None,

    "research": None,

    "final": None,

    "statistics": None,

    "thread_id": None,

    "waiting_for_approval": False,

    "research_running": False,

    "question": "",

    "messages": []
}


for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# =========================================================
# SIDEBAR
# =========================================================

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
    ].index(
        st.session_state.research_type
    )
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
    ].index(
        st.session_state.research_depth
    )
)


# =========================================================
# USER QUERY
# =========================================================

query = st.text_input(
    "🔎 Enter your research topic",
    value=st.session_state.query
)


# =========================================================
# RUN RESEARCH
# =========================================================

if st.button(
    "🚀 Start Research",
    type="primary"
):

    if not query.strip():

        st.warning(
            "Please enter a research topic."
        )

        st.stop()

    # Reset previous research
    st.session_state.query = query
    st.session_state.research_type = research_type
    st.session_state.research_depth = research_depth

    st.session_state.research = None
    st.session_state.final = None
    st.session_state.statistics = None

    st.session_state.research_plan = None

    # New LangGraph thread
    st.session_state.thread_id = str(
        uuid.uuid4()
    )

    st.session_state.research_running = True
    st.session_state.waiting_for_approval = False

    initial_state = {

        "query": query,

        "research_type": research_type,

        "research_depth": research_depth,

        "research_iterations": 0,

        "start_time": __import__(
            "time"
        ).time(),

        "messages": [
            HumanMessage(
                content=query
            )
        ]
    }

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    with st.spinner(
        "🧠 Creating research plan..."
    ):

        result = research_graph.invoke(
            initial_state,
            config=config
        )

    # =====================================================
    # HUMAN APPROVAL INTERRUPT
    # =====================================================

    snapshot = research_graph.get_state(
        config
    )

    interrupts = snapshot.tasks

    if interrupts:

        interrupt_value = None

        for task in interrupts:

            if getattr(
                task,
                "interrupts",
                None
            ):

                interrupt_value = (
                    task.interrupts[0].value
                )

                break

        if interrupt_value:

            st.session_state.research_plan = (
                interrupt_value.get(
                    "plan",
                    {}
                )
            )

            st.session_state.waiting_for_approval = True

            st.session_state.research_running = False

            st.rerun()


# =========================================================
# HUMAN APPROVAL UI
# =========================================================

if st.session_state.waiting_for_approval:

    st.divider()

    st.header(
        "👤 Human-in-the-Loop: Review Research Plan"
    )

    plan = st.session_state.research_plan or {}

    st.subheader("🎯 Research Objective")

    st.write(
        plan.get(
            "objective",
            "No objective generated."
        )
    )

    st.subheader("❓ Sub Questions")

    for index, question_item in enumerate(
        plan.get(
            "sub_questions",
            []
        ),
        start=1
    ):

        st.write(
            f"{index}. {question_item}"
        )

    st.subheader("🔎 Search Queries")

    for index, search_query in enumerate(
        plan.get(
            "search_queries",
            []
        ),
        start=1
    ):

        st.write(
            f"{index}. {search_query}"
        )

    st.subheader("🎯 Focus Areas")

    for focus in plan.get(
        "focus_areas",
        []
    ):

        st.write(
            f"• {focus}"
        )

    st.divider()

    feedback = st.text_area(
        "✏️ Optional feedback / modification",
        placeholder=(
            "Example: Add more focus on limitations "
            "and real-world applications."
        )
    )

    col1, col2 = st.columns(2)

    # =====================================================
    # APPROVE
    # =====================================================

    with col1:

        if st.button(
            "✅ Approve & Continue",
            type="primary"
        ):

            config = {
                "configurable": {
                    "thread_id": (
                        st.session_state.thread_id
                    )
                }
            }

            with st.spinner(
                "🔍 Continuing research..."
            ):

                research_graph.invoke(
                    Command(
                        resume={
                            "approved": True,
                            "feedback": feedback
                        }
                    ),
                    config=config
                )

            st.session_state.waiting_for_approval = False
            st.session_state.research_running = True

            st.rerun()

    # =====================================================
    # MODIFY
    # =====================================================

    with col2:

        if st.button(
            "✏️ Modify & Continue"
        ):

            if not feedback.strip():

                st.warning(
                    "Please provide modification feedback."
                )

                st.stop()

            # Ask the planner again using feedback
            modified_plan = dict(plan)

            modified_plan["human_feedback"] = feedback

            config = {
                "configurable": {
                    "thread_id": (
                        st.session_state.thread_id
                    )
                }
            }

            with st.spinner(
                "🔄 Updating research plan..."
            ):

                research_graph.invoke(
                    Command(
                        resume={
                            "approved": True,
                            "feedback": feedback,
                            "plan": modified_plan
                        }
                    ),
                    config=config
                )

            st.session_state.research_plan = modified_plan
            st.session_state.waiting_for_approval = False
            st.session_state.research_running = True

            st.rerun()


# =========================================================
# CHECK GRAPH COMPLETION
# =========================================================

if st.session_state.research_running:

    config = {
        "configurable": {
            "thread_id": (
                st.session_state.thread_id
            )
        }
    }

    snapshot = research_graph.get_state(
        config
    )

    if snapshot.values:

        values = snapshot.values

        if values.get(
            "final_report"
        ):

            st.session_state.final = (
                values.get(
                    "final_report"
                )
            )

            st.session_state.statistics = (
                values.get(
                    "statistics",
                    {}
                )
            )

            st.session_state.research = {

                "summary": values.get(
                    "analysis",
                    {}
                ).get(
                    "summary",
                    ""
                ),

                "insights": values.get(
                    "insights",
                    []
                ),

                "citations": values.get(
                    "sources",
                    []
                )
            }

            st.session_state.research_running = False

            st.success(
                "✅ Research completed successfully!"
            )

        elif values.get("error"):

            st.session_state.research_running = False

            st.error(
                values["error"]
            )


# =========================================================
# SIDEBAR STATISTICS
# =========================================================

if st.session_state.statistics:

    stats = st.session_state.statistics

    st.sidebar.divider()

    st.sidebar.header(
        "📊 Research Statistics"
    )

    st.sidebar.metric(
        "Sources Used",
        stats.get(
            "sources_used",
            0
        )
    )

    st.sidebar.metric(
        "Research Type",
        stats.get(
            "research_type",
            "-"
        )
    )

    st.sidebar.metric(
        "Research Depth",
        stats.get(
            "research_depth",
            "-"
        )
    )

    st.sidebar.metric(
        "Iterations",
        stats.get(
            "research_iterations",
            0
        )
    )

    st.sidebar.metric(
        "Time Taken",
        f"{stats.get('time_taken', 0)} sec"
    )

    st.sidebar.metric(
        "LLM",
        stats.get(
            "llm_model",
            "-"
        )
    )


# =========================================================
# REPORT
# =========================================================

if (
    st.session_state.final is not None
    and st.session_state.research is not None
):

    research = st.session_state.research
    final = st.session_state.final

    st.divider()

    st.header(
        "📄 Research Report"
    )

    # -----------------------------------------------------
    # Insights
    # -----------------------------------------------------

    with st.expander(
        "📊 Insights",
        expanded=True
    ):

        for insight in research.get(
            "insights",
            []
        ):

            st.write(
                f"✔️ {insight}"
            )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    with st.expander(
        "🧾 Research Summary"
    ):

        st.write(
            research.get(
                "summary",
                ""
            )
        )

    # -----------------------------------------------------
    # Introduction
    # -----------------------------------------------------

    with st.expander(
        "📖 Introduction"
    ):

        st.write(
            final.get(
                "introduction",
                ""
            )
        )

    # -----------------------------------------------------
    # Key Points
    # -----------------------------------------------------

    with st.expander(
        "🔑 Key Points"
    ):

        for point in final.get(
            "key_points",
            []
        ):

            st.write(
                f"👉 {point}"
            )

    # -----------------------------------------------------
    # Conclusion
    # -----------------------------------------------------

    with st.expander(
        "✅ Conclusion"
    ):

        st.write(
            final.get(
                "conclusion",
                ""
            )
        )

    # -----------------------------------------------------
    # Related Topics
    # -----------------------------------------------------

    with st.expander(
        "🧭 Related Topics"
    ):

        related_topics = final.get(
            "related_topics",
            []
        )

        if related_topics:

            for topic in related_topics:

                st.write(
                    f"🔹 {topic}"
                )

        else:

            st.write(
                "No related topics found."
            )

    # -----------------------------------------------------
    # Sources
    # -----------------------------------------------------

    with st.expander(
        "🔗 Sources"
    ):

        for link in final.get(
            "citations",
            []
        ):

            st.markdown(
                f"- {link}"
            )

    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    pdf_file = create_research_pdf(
        query=st.session_state.query,
        research=research,
        final=final
    )

    st.download_button(
        label="📥 Download Research PDF",
        data=pdf_file,
        file_name="research_report.pdf",
        mime="application/pdf"
    )


# =========================================================
# FOLLOW-UP CHAT
# =========================================================

st.divider()

st.subheader(
    "💬 Follow-up Chat"
)


question = st.text_input(
    "Ask a follow-up question",
    key="follow_up_question"
)


if st.button(
    "Ask",
    key="ask_follow_up"
):

    if st.session_state.final is None:

        st.warning(
            "⚠️ Please perform research first."
        )

        st.stop()

    if not question.strip():

        st.warning(
            "⚠️ Please enter a question."
        )

        st.stop()

    with st.spinner(
        "🤔 Thinking..."
    ):

        response = follow_up_chat(
            st.session_state.query,
            st.session_state.research,
            st.session_state.final,
            question
        )

    if "error" in response:

        st.error(
            response.get(
                "details",
                response.get(
                    "error",
                    "Unknown error"
                )
            )
        )

    else:

        st.success(
            "Answer"
        )

        st.write(
            response["answer"]
        )