import streamlit as st
import os
from fpdf import FPDF
import tempfile
# =====================================================
# SIMPLE LOGIN SYSTEM
# =====================================================

def login_page():
    st.markdown(
        """
        <style>
        .login-card {
            max-width: 420px;
            margin: 100px auto;
            padding: 2.5rem;
            border-radius: 16px;
            background: white;
            box-shadow: 0 12px 30px rgba(0,0,0,0.12);
        }
        .login-title {
            text-align: center;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .login-sub {
            text-align: center;
            color: #6b7280;
            margin-bottom: 1.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Academic Writing Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Secure Login</div>', unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):
        if username == "mahi" and password == "123456":
            st.session_state["logged_in"] = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown('</div>', unsafe_allow_html=True)

# Store PDF bytes safely between reruns
if "pdf_bytes" not in st.session_state:
    st.session_state["pdf_bytes"] = None
# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# If not logged in → STOP app here
if not st.session_state["logged_in"]:
    login_page()
    st.stop()
from sentence_scoring import (
    preprocess_sentence,
    calculate_ngram_probabilities,
    calculate_ngram_probabilities_backoff,  # ✅ ADD THIS
    sentence_log_probability,
    calculate_entropy,
    compute_fluency_score,
    fluency_label,
)
from language_model import preprocess_text, build_ngram_model

from letter_analyzer import (
    analyze_letter_application,
    generate_application_suggestions,
    generate_improvement_examples,
)

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Academic Writing Fluency Analyzer",
    layout="wide"
)

# =====================================================
# STYLES
# =====================================================
st.markdown("""
<style>
html, body {
    background-color: #ffffff;
    color: #1f2937;
    font-family: 'Segoe UI', sans-serif;
}
section[data-testid="stSidebar"] {
    background-color: #70cbdb;
    padding: 1.2rem;
}
.card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.score {
    font-size: 46px;
    font-weight: 800;
}
.good { color: #166534; }
.medium { color: #854d0e; }
.bad { color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# PATHS & CONFIG
# =====================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.path.join(BASE_DIR, "corpora")

MODE_CONFIG = {
    "General Academic": os.path.join(CORPUS_DIR, "general.txt"),
    "Statement of Purpose (SOP)": os.path.join(CORPUS_DIR, "sop.txt"),
    "Letter of Recommendation (LOR)": os.path.join(CORPUS_DIR, "lor.txt"),
}

# =====================================================
# SIDEBAR
# =====================================================
with st.sidebar:
    writing_context = st.selectbox("Writing Context", MODE_CONFIG.keys())
    ngram_mode = "Trigram"  # ✅ FORCE MODE
    st.markdown("**Language Model:** Bigram + Trigram (internal)")
    tool_mode = st.radio(
        "Select Tool",
        ["Sentence Analyzer", "Letter / Application Analyzer"]
    )

# =====================================================
# LOAD CORPUS & MODEL
# =====================================================
with open(MODE_CONFIG[writing_context], "r", encoding="utf-8") as f:
    corpus = f.read()

processed_corpus = preprocess_text(corpus)

bigram_counts, bigram_ctx, vocab_size = build_ngram_model(processed_corpus, 2)
trigram_counts, trigram_ctx, _ = build_ngram_model(processed_corpus, 3)  # ✅ ADD THIS

from fpdf import FPDF

def generate_application_pdf(result, writing_context):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Academic Writing Fluency Report", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Context: {clean_text_for_pdf(writing_context)}", ln=True)
    pdf.cell(0, 8, f"Overall Score: {result['document_score']}", ln=True)
    pdf.cell(
        0, 8,
        f"Assessment: {clean_text_for_pdf(result['document_label'])}",
        ln=True
    )

    pdf.ln(6)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, "Sentence Analysis", ln=True)

    pdf.set_font("Arial", "", 11)
    for s in result["sentence_results"]:
        sentence = clean_text_for_pdf(s["sentence"])
        label = clean_text_for_pdf(s["label"])

        pdf.multi_cell(
            0, 7,
            f"- {sentence}\n  Score: {s['score']} | {label}"
        )
        pdf.ln(1)

    # ✅ RETURN BYTES (NO FILE SYSTEM)
    return pdf.output(dest="S").encode("latin-1")

def clean_text_for_pdf(text: str) -> str:
    replacements = {
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "…": "...",
        "•": "-",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    return text.encode("latin-1", "ignore").decode("latin-1")
# =====================================================
# MAIN UI
# =====================================================
st.title("Academic Writing Fluency Analyzer")

# =====================================================
# SENTENCE ANALYZER
# =====================================================
if tool_mode == "Sentence Analyzer":

    sentence = st.text_area("Enter a sentence", height=120)

    if st.button("Analyze Sentence") and sentence.strip():

        tokens = preprocess_sentence(sentence)

        probs, low_probs = calculate_ngram_probabilities(
            tokens, 2, bigram_counts, bigram_ctx, vocab_size
        )

        log_p = sentence_log_probability(probs)
        entropy = calculate_entropy(probs)
        avg_lp = log_p / max(1, len(probs))

        score = compute_fluency_score(
            avg_lp, entropy, low_probs, writing_context
        )
        label = fluency_label(score)

        cls = (
            "good" if score >= 70
            else "medium" if score >= 50
            else "bad"
        )

        # ===== RESULT CARD =====
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="score {cls}">{score} / 100</div>',
            unsafe_allow_html=True
        )
        st.markdown(f"**Label:** {label}")
        st.write(f"Entropy: {round(entropy, 3)}")
        st.write(f"Avg Log Probability: {round(avg_lp, 3)}")

        if low_probs:
            st.write("Some phrasing may be uncommon in formal academic writing.")
        else:
            st.write("Sentence structure is fluent.")

        st.markdown("</div>", unsafe_allow_html=True)

        # ===== IMPROVEMENT EXAMPLES =====
        if score < 80:
            st.subheader("How to Improve")
            examples = generate_improvement_examples(sentence, score)
            for ex in examples:
                st.write("•", ex)

# =====================================================
# LETTER / APPLICATION ANALYZER
# =====================================================
# =====================================================
# LETTER / APPLICATION ANALYZER
# =====================================================
if tool_mode == "Letter / Application Analyzer":

    letter_text = st.text_area(
        "Paste full SOP / LOR / Application text",
        height=320
    )

    if st.button("Analyze Application") and letter_text.strip():

        scoring_functions = {
            "preprocess_sentence": preprocess_sentence,
            "calculate_ngram_probabilities": calculate_ngram_probabilities,
            "calculate_ngram_probabilities_backoff": calculate_ngram_probabilities_backoff,
            "sentence_log_probability": sentence_log_probability,
            "calculate_entropy": calculate_entropy,
            "compute_fluency_score": compute_fluency_score,
            "fluency_label": fluency_label,
        }

        result = analyze_letter_application(
            text=letter_text,
            writing_context=writing_context,
            ngram_mode="Trigram",
            processed_corpus=processed_corpus,
            bigram_counts=bigram_counts,
            bigram_ctx=bigram_ctx,
            trigram_counts=trigram_counts,
            trigram_ctx=trigram_ctx,
            vocab_size=vocab_size,
            scoring_functions=scoring_functions
        )

        if not result or result["total_sentences"] == 0:
            st.warning("No sentences could be analyzed.")
            st.session_state["pdf_bytes"] = None
        else:
            # ===== RESULT CARD =====
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### Overall Score: {result['document_score']}")
            st.markdown(f"**Assessment:** {result['document_label']}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### Suggestions")
            for s in generate_application_suggestions(result, writing_context):
                st.write("•", s)

            st.markdown("### Sentence Analysis")
            for s in result["sentence_results"]:
                if s["score"] < 70:
                    st.error(f"{s['sentence']}\nScore: {s['score']} | {s['label']}")
                else:
                    st.success(f"{s['sentence']}\nScore: {s['score']} | {s['label']}")

            # ===== GENERATE PDF (SAFE STORAGE) =====
            st.session_state["pdf_bytes"] = generate_application_pdf(
                result, writing_context
            )

    # ===== PDF DOWNLOAD BUTTON (SAFE & ALWAYS VISIBLE) =====
    if st.session_state["pdf_bytes"] is not None:
        st.download_button(
            label="📄 Download PDF Report",
            data=st.session_state["pdf_bytes"],
            file_name="academic_writing_analysis.pdf",
            mime="application/pdf"
        )


