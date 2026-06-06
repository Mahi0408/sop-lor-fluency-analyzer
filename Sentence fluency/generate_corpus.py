import random

subjects = [
    "I", "The student", "The applicant", "The candidate", "An individual",
    "A graduate", "The researcher", "The learner"
]

verbs = [
    "is pursuing", "is interested in", "is applying for", "aims to pursue",
    "plans to undertake", "is motivated to pursue", "seeks to gain",
    "intends to continue"
]

fields = [
    "higher education abroad",
    "advanced academic studies",
    "postgraduate education",
    "research opportunities",
    "professional development",
    "academic excellence",
    "interdisciplinary learning",
    "international education"
]

reasons = [
    "to enhance knowledge and skills",
    "to achieve long-term career goals",
    "to contribute meaningfully to society",
    "to gain global exposure",
    "to develop critical thinking abilities",
    "to strengthen research capabilities",
    "to expand academic horizons",
    "to grow both personally and professionally"
]

extras = [
    "through structured academic training.",
    "under the guidance of experienced faculty.",
    "in a rigorous learning environment.",
    "at a globally recognized institution.",
    "with access to modern research facilities.",
    "while engaging in collaborative learning.",
    "with a strong focus on innovation.",
    "supported by academic excellence."
]

def generate_sentence():
    return f"{random.choice(subjects)} {random.choice(verbs)} {random.choice(fields)} {random.choice(reasons)} {random.choice(extras)}"

def generate_corpus(lines=10000, output_file="corpus.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for _ in range(lines):
            f.write(generate_sentence() + "\n")

if __name__ == "__main__":
    generate_corpus(10000)
    print("✅ corpus.txt generated with 10,000 high-quality sentences")
