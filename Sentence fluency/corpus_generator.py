import os
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS_DIR = os.path.join(BASE_DIR, "corpora")

os.makedirs(CORPUS_DIR, exist_ok=True)

# =====================================================
# SENTENCE TEMPLATES
# =====================================================

GENERAL_SENTENCES = [
    "This study examines the impact of {} on {}.",
    "The results indicate a significant relationship between {} and {}.",
    "Previous research has explored the role of {} in {}.",
    "The findings contribute to a broader understanding of {}.",
    "This analysis highlights important trends in {}.",
    "The methodology applied in this research ensures {}.",
    "The study provides insights into {} and its implications.",
    "These results support existing theories related to {}.",
    "The research focuses on evaluating {} in detail.",
    "The discussion emphasizes the importance of {}."
]

SOP_SENTENCES = [
    "I am motivated to pursue advanced studies in {}.",
    "My academic background has prepared me for research in {}.",
    "I aim to develop expertise in {} through graduate study.",
    "My long term goal is to contribute to research in {}.",
    "This program aligns with my academic interests in {}.",
    "I have developed a strong foundation in {}.",
    "My experience has strengthened my interest in {}.",
    "I seek to expand my knowledge and skills in {}.",
    "Graduate study will allow me to explore {} in depth.",
    "I am committed to academic excellence in {}."
]

LOR_SENTENCES = [
    "The candidate has demonstrated strong abilities in {}.",
    "They consistently show dedication toward {}.",
    "Their academic performance reflects excellence in {}.",
    "The student possesses a strong aptitude for {}.",
    "They have shown remarkable growth in {}.",
    "The candidate approaches challenges in {} with maturity.",
    "Their contributions to {} are noteworthy.",
    "They exhibit professionalism and commitment in {}.",
    "The student has earned my highest recommendation for {}.",
    "Their skills in {} distinguish them from peers."
]

TOPICS = [
    "machine learning",
    "data analysis",
    "climate change",
    "academic research",
    "engineering systems",
    "computer science",
    "artificial intelligence",
    "statistical modeling",
    "scientific methodology",
    "graduate studies"
]

# =====================================================
# CORPUS GENERATION FUNCTION
# =====================================================
def generate_corpus(filename, templates, lines=10000):
    path = os.path.join(CORPUS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        for _ in range(lines):
            template = random.choice(templates)
            topic1 = random.choice(TOPICS)
            topic2 = random.choice(TOPICS)
            sentence = template.format(topic1, topic2)
            f.write(sentence + "\n")
    print(f"✅ Generated {lines} lines → {filename}")

# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    generate_corpus("general.txt", GENERAL_SENTENCES, 12000)
    generate_corpus("sop.txt", SOP_SENTENCES, 10000)
    generate_corpus("lor.txt", LOR_SENTENCES, 10000)
