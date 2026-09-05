from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import uuid

from HuggingFace.content_generator import generate_content
from HuggingFace.ppt.ppt_generator import generate_ppt_plan
from HuggingFace.ppt.ppt_renderer import render_ppt


app = FastAPI(
    title="Content Transformer API",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class TransformRequest(BaseModel):
    sourceText: str
    outputType: str
    tone: str = "Professional"
    audience: str = "Executive Leadership"


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "success": True,
        "message": "Backend is running"
    }


# --------------------------------------------------
# TEST
# --------------------------------------------------

@app.get("/api/test")
def test():
    return {
        "success": True,
        "message": "FastAPI test endpoint is working"
    }


@app.get("/api/confirm")
def confirm():
    return {
        "success": True,
        "message": "Frontend successfully connected to FastAPI!"
    }


# --------------------------------------------------
# TRANSFORM
# --------------------------------------------------

@app.post("/api/transform")
def transform(request: TransformRequest):

    # --------------------------------------------------
    # PPT
    # --------------------------------------------------

    if request.outputType == "PowerPoint":

        # Generate PPT presentation plan
        result = generate_ppt_plan(
            source_content=request.sourceText,
            target_audience=request.audience,
            tone=request.tone,
            language="English",
            detail_level="Medium",
            communication_objective="Inform",
            content_style="Clear and Structured"
        )

        # Check generation result
        if not result.get("success"):
            return {
                "success": False,
                "error": result.get(
                    "error",
                    "PPT generation failed."
                )
            }

        presentation = result.get("presentation")

        if not presentation:
            return {
                "success": False,
                "error": "PPT generator returned no presentation."
            }

        # --------------------------------------------------
        # RENDER PPTX
        # --------------------------------------------------

        output_dir = Path("generated_ppt")

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = f"presentation_{uuid.uuid4().hex}.pptx"

        output_path = output_dir / filename

        render_ppt(
            presentation_data=presentation,
            output_path=str(output_path)
        )

        return {
            "success": True,
            "outputType": "PowerPoint",
            "content": presentation,
            "file": str(output_path)
        }


    # --------------------------------------------------
    # OTHER CONTENT TYPES
    # --------------------------------------------------

    output_type_map = {
        "Summary": "executive_summary",
        "Advisory": "advisory",
        "LinkedIn Post": "linkedin_post",
        "Twitter/X Post": "twitter_post",
    }

    generator_output_type = output_type_map.get(
        request.outputType
    )

    # Check whether this is currently supported
    if not generator_output_type:
        return {
            "success": False,
            "error": (
                f"{request.outputType} "
                "generator is not connected yet."
            )
        }

    # Call existing content generator
    result = generate_content(
        source_content=request.sourceText,
        output_types=[generator_output_type],
        target_audience=request.audience,
        tone=request.tone,
    )

    output = result.get(
        generator_output_type
    )

    if not output:
        return {
            "success": False,
            "error": "Generator returned no result."
        }

    if not output.get("success"):
        return {
            "success": False,
            "error": output.get(
                "error",
                "Generation failed."
            )
        }

    return {
        "success": True,
        "outputType": request.outputType,
        "content": output["content"]
    }
