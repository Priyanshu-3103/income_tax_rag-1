import streamlit as st

from src.retrieval import retrieve
from src.llm import generate_answer
from src.guardrails import validate_question, validate_output


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TaxRules AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f5f7fb;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 8rem;
    }

    .title {
        font-size: 38px;
        font-weight: 750;
        color: #111827;
    }

    .subtitle {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .user-label,
    .assistant-label {
        font-size: 12px;
        font-weight: 700;
        color: #374151;
        margin-top: 18px;
        margin-bottom: 5px;
    }

    .user-box {
        background: #e5e7eb;
        color: #111827;
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 12px;
        font-size: 15px;
        line-height: 1.6;
    }

    .answer-box {
        background: white;
        color: #111827;
        border: 1px solid #e5e7eb;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 10px;
        font-size: 15px;
        line-height: 1.7;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }

    .verified {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        padding: 11px 15px;
        border-radius: 9px;
        margin-bottom: 10px;
        font-size: 13px;
    }

    .warning {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #9a3412;
        padding: 13px 16px;
        border-radius: 9px;
        margin-bottom: 10px;
        font-size: 14px;
    }

    .source-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 9px;
        padding: 12px;
        margin-bottom: 8px;
    }

    .source-title {
        font-weight: 700;
        color: #111827;
        font-size: 13px;
    }

    .source-meta {
        color: #6b7280;
        font-size: 12px;
        margin-top: 5px;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: #f9fafb;
    }

    .sidebar-title {
        font-size: 22px;
        font-weight: 750;
    }

    .sidebar-subtitle {
        color: #9ca3af !important;
        font-size: 12px;
        line-height: 1.5;
    }

    .status-card {
        background: #1f2937;
        padding: 12px;
        border-radius: 9px;
        margin-bottom: 8px;
    }

    .status-name {
        color: #9ca3af !important;
        font-size: 11px;
    }

    .status-value {
        color: #f9fafb !important;
        font-size: 13px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-title">
            ⚖️ TaxRules AI
        </div>

        <div class="sidebar-subtitle">
            Income-tax Rules 2026<br>
            Grounded RAG Assistant
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.markdown("### System Status")

    status = [
        ("Knowledge Base", "Income-tax Rules 2026"),
        ("Vector Database", "Qdrant"),
        ("Embedding Model", "MiniLM-L6-v2"),
        ("LLM", "Llama 3.2"),
    ]

    for name, value in status:

        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-name">{name}</div>
                <div class="status-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    st.markdown("### 🛡️ Guardrails")

    guards = [
        "✓ Input Validation",
        "✓ Prompt Injection Detection",
        "✓ Tax Domain Filtering",
        "✓ Retrieval Threshold",
        "✓ Citation Validation",
    ]

    for guard in guards:

        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-value">{guard}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="title">
        Income-tax Rules 2026 Assistant
    </div>

    <div class="subtitle">
        Ask questions about the Income-tax Rules 2026 and
        receive grounded answers with document citations.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

if len(st.session_state.messages) == 0:

    st.markdown("### 💡 Try asking")

    col1, col2, col3 = st.columns(3)

    with col1:
        example1 = st.button(
            "📄 Filing of Return",
            use_container_width=True
        )

    with col2:
        example2 = st.button(
            "💰 TDS Rules",
            use_container_width=True
        )

    with col3:
        example3 = st.button(
            "🧾 Tax Forms",
            use_container_width=True
        )

    if example1:
        st.session_state.pending_question = (
            "What is the procedure for filing a return of income?"
        )
        st.rerun()

    if example2:
        st.session_state.pending_question = (
            "What are the rules relating to TDS?"
        )
        st.rerun()

    if example3:
        st.session_state.pending_question = (
            "What forms are prescribed under the Income-tax Rules 2026?"
        )
        st.rerun()


# ============================================================
# DISPLAY PREVIOUS CONVERSATION
# ============================================================

for message in st.session_state.messages:

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    if message["role"] == "user":

        st.markdown(
            '<div class="user-label">👤 You</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="user-box">
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    elif message["role"] == "assistant":

        st.markdown(
            '<div class="assistant-label">🤖 TaxRules AI</div>',
            unsafe_allow_html=True
        )

        if message.get("warning"):

            st.markdown(
                f"""
                <div class="warning">
                    🛡️ <b>Guardrail Activated</b><br><br>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="answer-box">
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

            if message.get("verified"):

                st.markdown(
                    """
                    <div class="verified">
                        🛡️ <b>Grounded Response Verified</b><br>
                        Answer generated using retrieved document context.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ------------------------------------------------
            # SOURCES
            # ------------------------------------------------

            results = message.get("results", [])

            if results:

                with st.expander(
                    f"📚 Retrieved Sources ({len(results)})"
                ):

                    for i, result in enumerate(
                        results,
                        start=1
                    ):

                        st.markdown(
                            f"""
                            <div class="source-box">

                                <div class="source-title">
                                    📄 Source {i}
                                </div>

                                <div class="source-meta">
                                    Document:
                                    {result.get("source", "Unknown")}
                                    <br>
                                    PDF Page:
                                    {result.get("page", "Unknown")}
                                    <br>
                                    Chunk:
                                    {result.get("chunk_id", "Unknown")}
                                    <br>
                                    Retrieval Score:
                                    {result.get("score", 0):.4f}
                                </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        st.write(
                            result.get("text", "")
                        )


# ============================================================
# GET QUESTION
# ============================================================

pending_question = st.session_state.pop(
    "pending_question",
    None
)

user_question = st.chat_input(
    "Ask an Income-tax Rules 2026 question..."
)

if pending_question and not user_question:

    user_question = pending_question


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_question:

    # ========================================================
    # STEP 1 — SAVE USER QUESTION
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    # ========================================================
    # STEP 2 — INPUT GUARDRAIL
    # ========================================================

    valid, error = validate_question(
        user_question
    )

    if not valid:

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error,
                "warning": True
            }
        )

        st.rerun()


    # ========================================================
    # STEP 3 — RETRIEVAL
    # ========================================================

    with st.spinner(
        "🔎 Searching Income-tax Rules 2026..."
    ):

        results = retrieve(
            user_question
        )


    # ========================================================
    # STEP 4 — RETRIEVAL GUARDRAIL
    # ========================================================

    if not results:

        answer = (
            "I could not find sufficient information in the "
            "provided Income-tax Rules 2026 document."
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "warning": True
            }
        )

        st.rerun()


    # ========================================================
    # STEP 5 — BUILD CONTEXT
    # ========================================================

    context_parts = []

    for i, result in enumerate(
        results,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {i}

Source: {result["source"]}
PDF Page: {result["page"]}
Chunk ID: {result["chunk_id"]}
Retrieval Score: {result["score"]:.4f}

{result["text"]}
"""
        )

    context = "\n".join(
        context_parts
    )


    # ========================================================
    # STEP 6 — LLM
    # ========================================================

    with st.spinner(
        "🤖 Generating grounded answer..."
    ):

        answer = generate_answer(
            question=user_question,
            context=context
        )


    # ========================================================
    # STEP 7 — OUTPUT GUARDRAIL
    # ========================================================

    output_valid, output_error = validate_output(
        answer,
        results
    )


    if not output_valid:

        answer = (
            "I could not provide a reliable answer because "
            "the generated response could not be verified "
            "against the retrieved Income-tax Rules 2026 content."
        )

        verified = False

    else:

        verified = True


    # ========================================================
    # STEP 8 — SAVE COMPLETE RESPONSE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "results": results,
            "verified": verified,
            "warning": False
        }
    )


    # ========================================================
    # STEP 9 — RERENDER
    # ========================================================

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <hr>

    <div style="
        text-align:center;
        color:#9ca3af;
        font-size:11px;
        padding:15px;
    ">
        TaxRules AI • Income-tax Rules 2026 •
        Qdrant + Sentence Transformers + Ollama
    </div>
    """,
    unsafe_allow_html=True
)