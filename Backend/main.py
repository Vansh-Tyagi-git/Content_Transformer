from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from HuggingFace.content_generator import generate_content


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

    # Convert frontend names to generator names
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
            "error": f"{request.outputType} generator is not connected yet."
        }

    # Call your existing Python generator
    result = generate_content(
        source_content=request.sourceText,
        output_types=[generator_output_type],
        target_audience=request.audience,
        tone=request.tone,
    )

    output = result.get(generator_output_type)

    if not output:
        return {
            "success": False,
            "error": "Generator returned no result."
        }

    if not output.get("success"):
        return {
            "success": False,
            "error": output.get("error", "Generation failed.")
        }

    return {
        "success": True,
        "outputType": request.outputType,
        "content": output["content"]
    }
