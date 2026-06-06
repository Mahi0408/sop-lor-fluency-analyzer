import re
from collections import defaultdict


# -------------------------------
# PREPROCESSING
# -------------------------------

def preprocess_text(text):
    """
    Preprocess raw corpus text into a list of tokenized sentences.
    Training preprocessing MUST match test preprocessing.
    """
    text = text.lower()
    text = re.sub(r"[^a-z\s\.]", "", text)

    sentences = text.split(".")
    processed_sentences = []

    for sentence in sentences:
        words = sentence.strip().split()
        if words:
            processed_sentences.append(words)

    return processed_sentences


# -------------------------------
# N-GRAM GENERATION
# -------------------------------

def generate_ngrams(tokens, n):
    """
    Generate n-grams from a list of tokens.
    """
    return [tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


# -------------------------------
# MODEL TRAINING
# -------------------------------

def build_ngram_model(processed_sentences, n):
    """
    Builds n-gram and (n-1)-gram frequency counts.
    Returns:
      - ngram_counts
      - context_counts
      - vocabulary size
    """
    ngram_counts = defaultdict(int)
    context_counts = defaultdict(int)
    vocabulary = set()

    for sentence in processed_sentences:
        vocabulary.update(sentence)

        ngrams = generate_ngrams(sentence, n)
        contexts = generate_ngrams(sentence, n - 1) if n > 1 else []

        for ng in ngrams:
            ngram_counts[ng] += 1

        for ctx in contexts:
            context_counts[ctx] += 1

    return ngram_counts, context_counts, len(vocabulary)


# -------------------------------
# DEBUG TEST
# -------------------------------

if __name__ == "__main__":
    sample_text = "I am eating an apple. I am reading a book."

    processed = preprocess_text(sample_text)
    ngram_counts, context_counts, vocab_size = build_ngram_model(processed, 2)

    print("Sample bigram counts:")
    for k, v in list(ngram_counts.items())[:5]:
        print(k, ":", v)

    print("Vocabulary size:", vocab_size)
