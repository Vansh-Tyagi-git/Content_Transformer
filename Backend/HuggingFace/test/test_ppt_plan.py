from pathlib import Path
import sys
import json


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


# ============================================================
# IMPORTS
# ============================================================

from ppt.ppt_generator import generate_ppt_plan
from ppt.ppt_renderer import render_ppt


# ============================================================
# RICH TEST SOURCE CONTENT
# ============================================================

source_content = """
ARTIFICIAL INTELLIGENCE ADOPTION IN MODERN ORGANIZATIONS

Executive Overview

Artificial intelligence (AI) is becoming an increasingly important
technology for organizations across industries. Companies are using
AI to automate repetitive work, support employees, improve
decision-making, analyze large volumes of information, and increase
operational efficiency.

A successful AI strategy, however, requires more than simply
deploying AI tools. Organizations need to balance business value
with data privacy, cybersecurity, transparency, accountability, and
responsible implementation.

CURRENT STATE OF AI ADOPTION

Organizations are adopting AI across multiple business functions.
Common areas include customer service, marketing, finance, operations,
human resources, software development, and business intelligence.

A 2024 survey of organizations reported that 72% of organizations
had adopted AI in at least one business function, up from 55% in the
previous year.

Generative AI has accelerated adoption. Organizations are using
large language models and generative AI assistants for drafting
documents, summarizing information, generating software code,
research assistance, customer communication, and knowledge
management.

KEY BUSINESS BENEFITS

1. Automation of Repetitive Work

AI can automate repetitive and time-consuming activities such as
document processing, classification, data extraction, basic customer
support, and routine administrative tasks.

Automation allows employees to spend more time on higher-value
activities that require judgment, creativity, and human interaction.

2. Improved Decision-Making

AI can analyze large amounts of structured and unstructured data
and identify patterns that may be difficult to detect manually.

Organizations can use AI-supported analytics to improve forecasting,
identify anomalies, prioritize opportunities, and support operational
decisions.

3. Operational Efficiency

AI can optimize workflows and reduce manual effort across business
processes.

For example, organizations may use AI to route customer requests,
prioritize operational tasks, identify process bottlenecks, and
assist employees with information retrieval.

4. Employee Productivity

Generative AI tools can support employees with drafting,
summarization, research, coding assistance, content generation,
and internal knowledge discovery.

The goal should not be to replace human judgment in every process,
but to augment employees where AI can provide useful assistance.

AI USE CASES

Customer Service:
AI-powered assistants can handle common customer questions,
classify requests, summarize conversations, and route complex
issues to human representatives.

Software Development:
AI coding assistants can help developers generate code,
explain existing code, create tests, and identify potential issues.

Finance:
AI can support financial analysis, anomaly detection,
document processing, and forecasting activities.

Human Resources:
AI can assist with employee information retrieval, document
processing, workforce analytics, and administrative workflows.

Operations:
AI can help organizations optimize processes, forecast demand,
identify bottlenecks, and support operational planning.

MARKET AND BUSINESS IMPACT

Organizations are increasingly treating AI as a strategic capability
rather than an isolated technology experiment.

Companies that successfully integrate AI into business workflows
can potentially achieve faster processes, improved employee
productivity, better customer experiences, and more data-driven
decision-making.

However, technology adoption alone does not guarantee business
value. AI initiatives must be connected to clearly defined business
objectives and measurable outcomes.

KEY CHALLENGES

1. Data Privacy

AI systems may process sensitive customer, employee, financial,
or operational information. Organizations need controls that define
what information can be used with AI systems and how that information
is stored and processed.

2. Cybersecurity

AI systems introduce new security considerations. Organizations
must consider unauthorized access, data leakage, malicious inputs,
model misuse, and vulnerabilities in AI-enabled applications.

3. Transparency

Some AI systems can produce outputs that are difficult for users
to understand or explain.

Organizations should establish appropriate levels of transparency,
especially when AI influences important business decisions.

4. Accuracy and Reliability

AI systems can produce incorrect or misleading outputs.

Human review, validation processes, testing, and monitoring are
therefore important when AI is used in business-critical workflows.

5. Responsible Implementation

Organizations need to determine where AI should and should not
be used.

High-impact decisions may require stronger human oversight,
additional validation, and clearly defined accountability.

6. Employee Adoption

Employees may resist AI adoption because of concerns about job
security, changing responsibilities, lack of training, or uncertainty
about how AI will affect their work.

Organizations should involve employees early and provide appropriate
training and guidance.

AI GOVERNANCE

A responsible AI program should establish clear governance
structures covering the AI lifecycle.

Governance should address:

- Ownership and accountability
- Data governance
- Privacy requirements
- Security controls
- Model evaluation
- Testing and validation
- Human oversight
- Monitoring
- Incident management
- Documentation
- Regulatory and policy requirements

Governance should be proportional to the potential impact and risk
of each AI use case.

LOW-RISK AND HIGH-RISK USE CASES

Not every AI application requires the same level of control.

Low-risk examples may include:

- Internal document summarization
- Meeting-note generation
- Drafting internal communications
- Basic information retrieval

Higher-risk applications may include:

- Decisions affecting employees
- Financial decisions
- Customer eligibility decisions
- Safety-critical systems
- Processing highly sensitive information

Higher-risk applications require stronger review, testing,
monitoring, human oversight, and accountability.

IMPLEMENTATION ROADMAP

Organizations can approach AI adoption in stages.

Stage 1 — Identify Opportunities

Identify business problems where AI could provide measurable value.
Prioritize use cases based on expected benefits, feasibility,
data availability, and risk.

Stage 2 — Assess Risk

Evaluate privacy, security, accuracy, ethical, operational,
and regulatory risks associated with each use case.

Stage 3 — Run Controlled Pilots

Start with limited pilots rather than immediately deploying AI
across the entire organization.

Define success criteria and measure results.

Stage 4 — Validate Results

Evaluate whether the AI solution delivers the expected business
outcomes.

Measure factors such as time saved, productivity improvements,
accuracy, adoption, cost impact, and user satisfaction where
appropriate.

Stage 5 — Scale Responsibly

Successful use cases can be expanded after appropriate technical,
security, governance, and operational reviews.

Stage 6 — Monitor Continuously

AI systems should be monitored after deployment.

Organizations should review performance, accuracy, security,
user feedback, incidents, and changes in business requirements.

MEASURING SUCCESS

AI programs should use measurable objectives rather than focusing
only on the number of AI tools deployed.

Potential measures include:

- Reduction in processing time
- Employee productivity
- Cost reduction
- Customer response time
- Accuracy improvements
- Adoption rates
- User satisfaction
- Number of successfully automated tasks
- Risk and incident rates

A successful AI initiative should demonstrate both business value
and responsible operation.

RECOMMENDATIONS

Organizations should:

1. Start with clearly defined business problems rather than
   adopting AI simply because the technology is available.

2. Prioritize use cases based on business value, feasibility,
   data readiness, and risk.

3. Establish AI governance before scaling high-impact use cases.

4. Maintain appropriate human oversight for decisions where
   AI errors could have significant consequences.

5. Train employees on how to use AI tools effectively and
   responsibly.

6. Establish security and privacy controls for AI systems.

7. Measure AI initiatives using clear business and operational
   outcomes.

8. Continuously monitor deployed AI systems and update controls
   as risks and requirements change.

KEY TAKEAWAY

AI can create significant organizational value through automation,
decision support, productivity improvements, and operational
efficiency.

At the same time, organizations must address privacy, security,
transparency, accuracy, accountability, and responsible-use
challenges.

The strongest AI strategies combine technology adoption with
business objectives, employee enablement, measurable outcomes,
and appropriate governance.

The objective is not simply to deploy more AI.

The objective is to deploy AI where it creates meaningful value
while maintaining appropriate levels of human oversight,
security, accountability, and trust.
"""


# ============================================================
# OUTPUT PATHS
# ============================================================

OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_PPTX = OUTPUT_DIR / "ai_adoption_presentation.pptx"
OUTPUT_JSON = OUTPUT_DIR / "ai_adoption_presentation.json"


# ============================================================
# GENERATE PRESENTATION PLAN
# ============================================================

print("\n" + "=" * 70)
print("GENERATING PPT PLAN")
print("=" * 70)

result = generate_ppt_plan(
    source_content=source_content,
    target_audience="Business and Technology Professionals",
    tone="Professional and Informative",
    language="English",
    detail_level="Medium",
    communication_objective="Educate",
    content_style="Clear and Engaging"
)


# ============================================================
# HANDLE GENERATION FAILURE
# ============================================================

if not result.get("success"):

    print("\n" + "=" * 70)
    print("PPT PLAN GENERATION FAILED")
    print("=" * 70)

    print("\nError:")
    print(result.get("error", "Unknown error"))

    if result.get("raw_response"):

        print("\nRaw DeepSeek Response:")
        print(result["raw_response"])

    sys.exit(1)


# ============================================================
# GET PRESENTATION
# ============================================================

presentation = result["presentation"]


# ============================================================
# PRINT FULL JSON
# ============================================================

print("\n" + "=" * 70)
print("GENERATED PRESENTATION JSON")
print("=" * 70)

print(
    json.dumps(
        presentation,
        indent=4,
        ensure_ascii=False
    )
)


# ============================================================
# SAVE JSON
# ============================================================

try:

    with open(
        OUTPUT_JSON,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            presentation,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nJSON saved to:")
    print(OUTPUT_JSON)

except Exception as e:

    print("\nFailed to save JSON:")
    print(str(e))


# ============================================================
# PRINT SLIDE SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SLIDE SUMMARY")
print("=" * 70)

for slide in presentation["slides"]:

    print("\n" + "-" * 70)

    print(
        f"Slide {slide['slide_number']}: "
        f"{slide['title']}"
    )

    print(
        f"Layout: {slide['layout']}"
    )

    if slide.get("subtitle"):

        print(
            f"Subtitle: {slide['subtitle']}"
        )

    if slide.get("content"):

        print("Content:")

        for item in slide["content"]:

            if isinstance(item, dict):

                print(
                    "  - "
                    + json.dumps(
                        item,
                        ensure_ascii=False
                    )
                )

            else:

                print(
                    f"  - {item}"
                )

    if slide.get("left_content"):

        print("Left Content:")

        for item in slide["left_content"]:

            print(
                f"  - {item}"
            )

    if slide.get("right_content"):

        print("Right Content:")

        for item in slide["right_content"]:

            print(
                f"  - {item}"
            )

    visual = slide.get(
        "visual",
        {}
    )

    print("Visual:")
    print(
        f"  Type: {visual.get('type', 'none')}"
    )
    print(
        f"  Description: "
        f"{visual.get('description', '')}"
    )


# ============================================================
# RENDER POWERPOINT
# ============================================================

print("\n" + "=" * 70)
print("RENDERING POWERPOINT")
print("=" * 70)

try:

    output_path = render_ppt(
        presentation_data=presentation,
        output_path=str(OUTPUT_PPTX)
    )

    print("\nPowerPoint generated successfully.")

    print(
        f"File: {output_path}"
    )

    if Path(output_path).exists():

        file_size = Path(
            output_path
        ).stat().st_size

        print(
            f"Size: {file_size:,} bytes"
        )

except Exception as e:

    print("\n" + "=" * 70)
    print("POWERPOINT RENDERING FAILED")
    print("=" * 70)

    print(
        f"Error: {str(e)}"
    )

    sys.exit(1)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 70)
print("TEST COMPLETED SUCCESSFULLY")
print("=" * 70)

print(
    f"\nJSON : {OUTPUT_JSON}"
)

print(
    f"PPTX : {OUTPUT_PPTX}"
)

print("\n")