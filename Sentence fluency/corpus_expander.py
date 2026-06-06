import random
import itertools

# ================================
# CONFIGURATION
# ================================

TARGET_SIZES = {
    "general_academic.txt": 50000,
    "sop.txt": 30000,
    "lor.txt": 30000
}

CORPUS_DIR = "corpora"


# ================================
# UTILITY FUNCTIONS
# ================================

def load_sentences(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


def save_sentences(path, sentences):
    with open(path, "w", encoding="utf-8") as f:
        for s in sentences:
            f.write(s + "\n")


def expand_sentences(base_sentences, target_size):
    expanded = []
    cycle = itertools.cycle(base_sentences)

    while len(expanded) < target_size:
        sentence = next(cycle)

        if sentence.endswith("."):
            sentence = sentence[:-1]

        variations = [
            sentence + ".",
            sentence + " for academic purposes.",
            "In academic contexts, " + sentence.lower() + ".",
            sentence + " in higher education.",
        ]

        expanded.extend(variations)

    return expanded[:target_size]


# ================================
# MAIN PIPELINE
# ================================

def main():
    for file_name, target_size in TARGET_SIZES.items():
        path = f"{CORPUS_DIR}/{file_name}"

        print(f"Processing {file_name}...")

        base_sentences = load_sentences(path)

        if len(base_sentences) < 100:
            raise ValueError(
                f"{file_name} has too few sentences. "
                f"Add more seed sentences before expansion."
            )

        expanded = expand_sentences(base_sentences, target_size)
        save_sentences(path, expanded)

        print(f"✔ {file_name} expanded to {len(expanded)} lines")

    print("\nAll corpora expanded successfully.")


if __name__ == "__main__":
    main()
