from content_generator import generate_content


# ============================================================
# TEST SOURCE CONTENT
# ============================================================

source_content = """
Artificial intelligence is increasingly being adopted by organizations
to automate repetitive tasks, improve decision-making and enhance
operational efficiency.

However, AI adoption also introduces challenges related to data privacy,
security, transparency and responsible implementation.

Organizations need appropriate governance frameworks to ensure that
AI systems are used responsibly while maximizing their potential benefits.
"""


# ============================================================
# SELECT OUTPUTS TO TEST
# ============================================================

selected_outputs = [
    "linkedin_post",
    "twitter_post",
    "advisory",
    "executive_summary"
]


# ============================================================
# GENERATE CONTENT
# ============================================================

generated_results = generate_content(
    source_content=source_content,
    output_types=selected_outputs,
    target_audience="Business and Technology Professionals",
    tone="Professional and Informative",
    language="English",
    detail_level="Medium",
    communication_objective="Educate",
    content_style="Clear and Engaging"
)


# ============================================================
# PRINT RESULTS
# ============================================================

for output_type, result in generated_results.items():

    print("\n")
    print("=" * 70)
    print(f"OUTPUT TYPE: {output_type.upper()}")
    print("=" * 70)

    if result["success"]:
        print(result["content"])
    else:
        print("ERROR:", result["error"])
