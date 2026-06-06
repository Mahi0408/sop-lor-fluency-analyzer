import math
import re
from language_model import generate_ngrams

# =====================================================
# PREPROCESS
# =====================================================
def preprocess_sentence(sentence):
    sentence = sentence.lower()
    sentence = re.sub(r"[^a-z\s]", "", sentence)
    return sentence.split()


# =====================================================
# BIGRAM
# =====================================================
def calculate_ngram_probabilities(
    tokens, n, ngram_counts, context_counts, vocab_size, smoothing=True
):
    probs, low = [], []
    ngrams = generate_ngrams(tokens, n)

    for ng in ngrams:
        ctx = ng[:-1]
        c_ng = ngram_counts.get(ng, 0)
        c_ctx = context_counts.get(ctx, 0)

        p = (c_ng + 1) / (c_ctx + vocab_size)
        probs.append(p)

        if p < 0.003:
            low.append((ng, p))

    return probs, low


# =====================================================
# TRIGRAM + BACKOFF
# =====================================================
COMMON_TRIGRAMS = {
    ("one", "of", "the"),
    ("has", "become", "one"),
    ("as", "well", "as"),
    ("in", "order", "to")
}

def calculate_ngram_probabilities_backoff(
    tokens,
    bigram_counts,
    bigram_ctx,
    trigram_counts,
    trigram_ctx,
    vocab_size
):
    probs, low = [], []
    trigrams = generate_ngrams(tokens, 3)

    for tg in trigrams:
        ctx = tg[:-1]
        c_tg = trigram_counts.get(tg, 0)
        c_ctx = trigram_ctx.get(ctx, 0)

        if c_ctx > 0:
            p = (c_tg + 1) / (c_ctx + vocab_size)
        else:
            bg = tg[1:]
            bg_ctx = bg[:-1]
            p = (bigram_counts.get(bg, 0) + 1) / (bigram_ctx.get(bg_ctx, 0) + vocab_size)

        probs.append(p)

        if p < 0.002 and tg not in COMMON_TRIGRAMS:
            low.append((tg, p))

    return probs, low


# =====================================================
# METRICS
# =====================================================
def sentence_log_probability(probs):
    return sum(math.log(p) for p in probs if p > 0) if probs else -15


def calculate_entropy(probs):
    return -sum(math.log2(p) for p in probs) / len(probs) if probs else 1.0


# =====================================================
# FLUENCY SCORE (IMPROVED)
# =====================================================
def compute_fluency_score(avg_log_prob, entropy, low_prob_ngrams, writing_context):
    """
    Academic-calibrated fluency scoring.
    Designed so strong academic sentences score 70–90.
    """

    # -------------------------------------------------
    # Base score: solid academic English
    # -------------------------------------------------
    score = 80

    # -------------------------------------------------
    # Log probability (very gentle, stabilised)
    # Typical academic avg_log_prob ≈ -3.5 to -5.5
    # -------------------------------------------------
    score += avg_log_prob * 1.2   # gentle influence

    # -------------------------------------------------
    # Entropy penalty (only when unusually high)
    # -------------------------------------------------
    if entropy > 7.0:
        score -= min((entropy - 7.0) * 1.8, 6)

    # -------------------------------------------------
    # Rare n-gram penalty (soft + capped)
    # -------------------------------------------------
    rare_penalty = min(len(low_prob_ngrams), 3)
    score -= rare_penalty * 1.5

    # -------------------------------------------------
    # Writing context adjustment
    # -------------------------------------------------
    if writing_context == "Statement of Purpose (SOP)":
        score += 3
    elif writing_context == "Letter of Recommendation (LOR)":
        score += 4
    else:  # General Academic
        score += 2

    # -------------------------------------------------
    # Clamp to [0, 100]
    # -------------------------------------------------
    return round(max(0, min(100, score)), 2)


def fluency_label(score, writing_context=None):
    if score >= 70:
        return "Highly Fluent"
    elif score >= 50:
        return "Moderately Fluent"
    else:
        return "Needs Improvement"