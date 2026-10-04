# app.py

import asyncio

import streamlit as st

from src.agent.agent import MovieAgent
from src.agent.schemas import AgentRequest
from src.retrieval.vector_store import VectorStore


st.set_page_config(
    page_title="Movie Intelligence Assistant",
    page_icon="🎬",
    layout="wide",
)


st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            font-size: 1.05rem;
            color: #666;
            margin-bottom: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_vector_store():
    return VectorStore()


@st.cache_data
def get_movies():
    vector_store = get_vector_store()
    return vector_store.get_movies()


def get_agent():
    """
    Create one MovieAgent per Streamlit user session.

    This is important because MovieAgent contains ConversationState.
    Using st.cache_resource here would share the same conversation
    state between users.
    """
    if "movie_agent" not in st.session_state:
        st.session_state.movie_agent = MovieAgent()

    return st.session_state.movie_agent


def run_agent(
    agent: MovieAgent,
    request: AgentRequest,
) -> dict:
    return asyncio.run(
        agent.process(request)
    )


def main():
    st.markdown(
        '<div class="main-title">🎬 Movie Intelligence Assistant</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="subtitle">
            Ask questions about movies using subtitle-based
            Retrieval-Augmented Generation.
        </div>
        """,
        unsafe_allow_html=True,
    )

    movies = get_movies()

    if not movies:
        st.error(
            "No movies are currently indexed in ChromaDB."
        )
        return

    agent = get_agent()

    with st.sidebar:
        st.header("🎥 Movie")

        movie = st.selectbox(
            "Select a movie",
            options=movies,
        )

        st.divider()

        st.header("⚙️ Action")

        action = st.radio(
            "What would you like to do?",
            options=[
                "Ask a question",
                "Email the answer",
            ],
        )

        st.divider()

        st.caption(
            f"📚 {len(movies)} movies indexed"
        )

        st.caption(
            "Powered by RAG + ChromaDB + Qwen2.5 + MCP"
        )

    st.subheader("What would you like to know?")

    query = st.text_area(
        "Question",
        placeholder=(
            "Example: What does Thanos want from the Avengers?"
        ),
        height=120,
        label_visibility="collapsed",
    )

    recipient = None

    if action == "Email the answer":
        st.subheader("Email")

        recipient = st.text_input(
            "Recipient email address",
            placeholder="example@gmail.com",
        )

        st.caption(
            'For a follow-up, you can enter "Email me that" '
            "to email your previous answer."
        )

    st.write("")

    submit_label = (
        "🔍 Ask Question"
        if action == "Ask a question"
        else "📧 Generate & Send Email"
    )

    submitted = st.button(
        submit_label,
        type="primary",
        use_container_width=True,
    )

    if not submitted:
        return

    query = query.strip()

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------

    if not query:
        st.warning(
            "Please enter a question or follow-up request."
        )
        return

    if action == "Email the answer":
        # Do not require the recipient here for "Email me that".
        # The agent itself will ask for the recipient and preserve
        # the pending action in ConversationState.
        is_follow_up = agent._is_email_follow_up(query)

        if not is_follow_up:
            if not recipient or not recipient.strip():
                st.warning(
                    "Please enter an email address."
                )
                return

    intent = (
        "information"
        if action == "Ask a question"
        else "email"
    )

    request = AgentRequest(
        intent=intent,
        movie=movie,
        query=query,
        recipient=(
            recipient.strip()
            if recipient and recipient.strip()
            else None
        ),
    )

    with st.spinner(
        "Searching subtitles and generating an answer..."
    ):
        try:
            result = run_agent(
                agent,
                request,
            )

        except Exception as exc:
            st.error(
                f"An unexpected error occurred: "
                f"{type(exc).__name__}: {exc}"
            )
            return

    st.divider()

    status = result.get("status")

    # ---------------------------------------------------------
    # Successful result
    # ---------------------------------------------------------

    if status == "success":

        st.subheader("💡 Answer")

        with st.container(border=True):
            st.write(result["answer"])

        citations = result.get(
            "citations",
            [],
        )

        with st.expander(
            f"📚 Sources ({len(citations)})"
        ):
            if citations:
                for citation in citations:
                    st.write(
                        f"• {citation}"
                    )
            else:
                st.write(
                    "No citations available."
                )

        # -----------------------------------------------------
        # Debug evidence
        # -----------------------------------------------------

        with st.expander(
            "🔧 Debug: Retrieved Evidence"
        ):

            evidence = result.get(
                "evidence",
                [],
            )

            if not evidence:
                st.write(
                    "No evidence was returned."
                )

            else:
                for index, item in enumerate(
                    evidence,
                    start=1,
                ):

                    st.markdown(
                        f"### Evidence {index}"
                    )

                    st.write(
                        f"**Movie:** "
                        f"{item.get('movie')}"
                    )

                    st.write(
                        f"**Chunk:** "
                        f"{item.get('chunk_id')}"
                    )

                    st.write(
                        f"**Timestamp:** "
                        f"{item.get('start_time')} → "
                        f"{item.get('end_time')}"
                    )

                    st.write(
                        f"**Distance:** "
                        f"{item.get('score')}"
                    )

                    st.write(
                        f"**Text:** "
                        f"{item.get('text')}"
                    )

                    st.divider()

        if result.get("route") == "email":
            st.success(
                result.get(
                    "email_result",
                    "Email sent successfully.",
                )
            )

    # ---------------------------------------------------------
    # Clarification
    # ---------------------------------------------------------

    elif status == "clarification":

        st.warning(
            f"❓ "
            f"{result.get(
                'message',
                'More information is required.',
            )}"
        )

    # ---------------------------------------------------------
    # Movie not found
    # ---------------------------------------------------------

    elif status == "not_found":

        st.error(
            f"❌ "
            f"{result.get(
                'message',
                'Movie not found.',
            )}"
        )

    # ---------------------------------------------------------
    # No evidence
    # ---------------------------------------------------------

    elif status == "no_evidence":

        st.warning(
            "⚠️ "
            + result.get(
                "message",
                "No sufficient evidence was found.",
            )
        )

    # ---------------------------------------------------------
    # No previous result
    # ---------------------------------------------------------

    elif status == "no_previous_result":

        st.warning(
            "⚠️ "
            + result.get(
                "message",
                "There is no previous answer available.",
            )
        )

    # ---------------------------------------------------------
    # Unexpected status
    # ---------------------------------------------------------

    else:

        st.error(
            result.get(
                "message",
                "The request could not be completed.",
            )
        )


if __name__ == "__main__":
    main()