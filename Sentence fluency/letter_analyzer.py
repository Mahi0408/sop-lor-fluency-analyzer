import re

# =====================================================
# SENTENCE SPLITTING
# =====================================================
def split_into_sentences(text):
    """
    STEP 1: Safe sentence extraction for application analysis.
    """
    if not text or not isinstance(text, str):
        return []

    # Normalize whitespace (very important for SOP/LOR)
    text = re.sub(r"\s+", " ", text.strip())

    # Split on sentence-ending punctuation
    raw_sentences = re.split(r"[.!?]+", text)

    sentences = []
    for s in raw_sentences:
        s = s.strip()
        # Ignore junk / very short fragments
        if len(s.split()) >= 4:
            sentences.append(s)

    return sentences

# =====================================================
# SINGLE SENTENCE ANALYSIS
# =====================================================
def analyze_single_sentence(
    sentence,
    writing_context,
    ngram_mode,
    bigram_counts,
    bigram_ctx,
    trigram_counts,
    trigram_ctx,
    vocab_size,
    scoring_functions
):
    # ---- HARD SAFETY CHECK ----
    if not scoring_functions or not isinstance(scoring_functions, dict):
        return None

    required_keys = [
        "preprocess_sentence",
        "calculate_ngram_probabilities",
        "calculate_ngram_probabilities_backoff",
        "sentence_log_probability",
        "calculate_entropy",
        "compute_fluency_score",
        "fluency_label",
    ]

    for k in required_keys:
        if k not in scoring_functions:
            return None

    preprocess_sentence = scoring_functions["preprocess_sentence"]
    calc_bigram = scoring_functions["calculate_ngram_probabilities"]
    calc_backoff = scoring_functions["calculate_ngram_probabilities_backoff"]
    log_prob_fn = scoring_functions["sentence_log_probability"]
    entropy_fn = scoring_functions["calculate_entropy"]
    score_fn = scoring_functions["compute_fluency_score"]
    label_fn = scoring_functions["fluency_label"]

    tokens = preprocess_sentence(sentence)
    tokens = preprocess_sentence(sentence)
    if not tokens:
     return {
        "sentence": sentence,
        "score": 60.0,
        "label": "Moderately Fluent",
        "entropy": 0.0,
        "avg_log_prob": 0.0,
        "low_ngrams": []
    }

    # ---- NGRAM MODE ----
    if ngram_mode == "Bigram":
        probs, low = calc_bigram(
            tokens, 2, bigram_counts, bigram_ctx, vocab_size
        )
    else:
        probs, low = calc_backoff(
            tokens,
            bigram_counts, bigram_ctx,
            trigram_counts, trigram_ctx,
            vocab_size
        )

    log_p = log_prob_fn(probs)
    entropy = entropy_fn(probs)
    #avg_lp = log_p / max(1, len(probs))
    avg_lp = log_p / max(3, len(tokens))

    score = score_fn(avg_lp, entropy, low, writing_context)

    return {
        "sentence": sentence,
        "score": round(score, 2),
        "label": label_fn(score),
        "entropy": round(entropy, 3),
        "avg_log_prob": round(avg_lp, 3),
        "low_ngrams": low
    }

# =====================================================
# FULL LETTER / APPLICATION ANALYSIS
# =====================================================
def analyze_letter_application(
    text,
    writing_context,
    ngram_mode,
    processed_corpus,  # kept for future use
    bigram_counts,
    bigram_ctx,
    trigram_counts,
    trigram_ctx,
    vocab_size,
    scoring_functions
):
    sentences = split_into_sentences(text)
    results = []

    for s in sentences:
        r = analyze_single_sentence(
            s,
            writing_context,
            ngram_mode,
            bigram_counts,
            bigram_ctx,
            trigram_counts,
            trigram_ctx,
            vocab_size,
            scoring_functions
        )
        if r:
            results.append(r)

    # ✅ FIX 1: this must be AFTER the loop
    if not results:
        return {
            "document_score": 0,
            "document_label": "Needs Improvement",
            "document_explanation": "No sentences could be reliably analyzed.",
            "sentence_results": [],
            "weak_sentences": [],
            "total_sentences": 0
        }

    scores = [r["score"] for r in results]
    document_score = round(sum(scores) / len(scores), 2)

    if document_score >= 70:
        document_label = "Highly Fluent Application"
        explanation = (
            "The application demonstrates strong academic fluency, "
            "consistent sentence control, and appropriate academic phrasing."
        )
    elif document_score >= 55:
        document_label = "Moderately Fluent Application"
        explanation = (
            "The application is generally clear but contains sentences "
            "that rely on abstract or less precise phrasing."
        )
    else:
        document_label = "Needs Improvement"
        explanation = (
            "The application contains multiple sentences that deviate from "
            "typical academic sentence patterns found in the corpus."
        )

    return {
        "document_score": document_score,
        "document_label": document_label,
        "document_explanation": explanation,   # ✅ FIX 2
        "sentence_results": results,
        "weak_sentences": [r for r in results if r["score"] < 70],
        "total_sentences": len(results)
    }

def analyze_application_structure(sentence_results):
    """
    STEP 4: High-level academic diagnostics for applications
    Uses sentence statistics only (safe, no new models)
    """

    if not sentence_results:
        return []

    scores = [s["score"] for s in sentence_results]
    low_ngram_counts = [len(s["low_ngrams"]) for s in sentence_results]
    entropies = [s["entropy"] for s in sentence_results]

    feedback = []

    # ---- CONSISTENCY ----
    if max(scores) - min(scores) > 15:
        feedback.append(
            "Sentence fluency varies noticeably. Academic writing benefits from consistent sentence control."
        )

    # ---- PRECISION ----
    if sum(low_ngram_counts) / len(scores) > 1.5:
        feedback.append(
            "Several sentences rely on uncommon phrasing. Replace abstract or conversational expressions with discipline-neutral academic terms."
        )

    # ---- CLARITY ----
    avg_entropy = sum(entropies) / len(entropies)
    if avg_entropy > 6.5:
        feedback.append(
            "Some sentences may be structurally dense. Academic corpora favor clear subject–verb–object constructions."
        )

    if not feedback:
        feedback.append(
            "The application demonstrates strong academic fluency and stylistic consistency."
        )

    return feedback
# STEP 4: Structural academic feedback
    structure_feedback = analyze_application_structure(result["sentence_results"])
    suggestions.extend(structure_feedback)

# =====================================================
# APPLICATION-LEVEL SUGGESTIONS
# =====================================================
def generate_application_suggestions(result, writing_context):
    suggestions = []

    if len(result["weak_sentences"]) >= 2:
        suggestions.append(
            "Several sentences rely on abstract phrasing. Academic writing favors precise claims and explicit relationships."
        )

    if writing_context == "Statement of Purpose (SOP)":
        suggestions.append(
            "Explicitly connect motivation, academic background, and research objectives."
        )

    if writing_context == "Letter of Recommendation (LOR)":
        suggestions.append(
            "Use concrete examples to support evaluative statements."
        )

    if not suggestions:
        suggestions.append(
            "Overall fluency is strong. Minor stylistic refinements may improve clarity."
        )

        

    return suggestions

# =====================================================
# IMPROVEMENT EXAMPLES (SINGLE, CANONICAL VERSION)
# =====================================================
def generate_improvement_examples(sentence, score):
    examples = []

    if score >= 70:
        examples.append(
            "This sentence aligns well with formal academic writing found in the corpus."
        )
        examples.append(
            "Minor refinements may include tightening clauses or reducing adjective density."
        )
        return examples

    # Below 70 → explanation required
    examples.append(
        "The sentence is grammatically correct but relies on broad or abstract phrasing."
    )
    examples.append(
        "Academic corpora favor explicit agents, precise verbs, and clearly stated outcomes."
    )

    examples.append("Example revision:")
    examples.append("• Original: " + sentence)
    examples.append(
        "• Improved: Climate change poses a significant threat to global food security by disrupting agricultural productivity and supply chains."
    )

    

    return examples