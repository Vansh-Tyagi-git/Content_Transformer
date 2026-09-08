from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import uuid
import mimetypes

from AiVideoGenerator.main import generate_video
from HuggingFace.content_generator import generate_content
from HuggingFace.ppt.ppt_generator import generate_ppt_plan
from HuggingFace.ppt.ppt_renderer import render_ppt
from HuggingFace.InfoGraph import generate_infographic


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PPT_DIR = BASE_DIR / "generated_ppt"
VIDEO_DIR = BASE_DIR / "generated_video"

PPT_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Content Transformer API",
    version="1.1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",

        # Vercel
        "https://content-transformer-krda1geqn-vanshs-projects-367523d4.vercel.app",
        "https://content-transformer-steel.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STATIC GENERATED FILES
# ============================================================

# PPT files:
# http://127.0.0.1:8000/generated-ppt/file.pptx

app.mount(
    "/generated-ppt",
    StaticFiles(directory=str(PPT_DIR)),
    name="generated-ppt"
)


# Video files:
# http://127.0.0.1:8000/generated-video/file.mp4

app.mount(
    "/generated-video",
    StaticFiles(directory=str(VIDEO_DIR)),
    name="generated-video"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class TransformRequest(BaseModel):

    sourceText: str

    outputType: str

    tone: str = "Professional"

    audience: str = "Executive Leadership"

    duration: int = 60


# ============================================================
# HELPER
# ============================================================

def public_asset(
    request: Request,
    route: str,
    path: Path
) -> dict:

    url = (
        f"{str(request.base_url).rstrip('/')}"
        f"/{route}/{path.name}"
    )

    media_type = (
        mimetypes.guess_type(path.name)[0]
        or "application/octet-stream"
    )

    return {
        "name": path.name,
        "url": url,
        "download_url": url,
        "preview_url": url,
        "media_type": media_type,
    }


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "success": True,
        "message": "Backend is running"
    }


# ============================================================
# TEST
# ============================================================

@app.get("/api/test")
def test():

    return {
        "success": True,
        "message": "FastAPI test endpoint is working"
    }


# ============================================================
# CONFIRM FRONTEND CONNECTION
# ============================================================

@app.get("/api/confirm")
def confirm():

    return {
        "success": True,
        "message": "Frontend successfully connected to FastAPI!"
    }


# ============================================================
# TRANSFORM
# ============================================================

@app.post("/api/transform")
def transform(
    request: TransformRequest,
    http_request: Request
):

    # --------------------------------------------------------
    # Validate source
    # --------------------------------------------------------

    if not request.sourceText.strip():

        return {
            "success": False,
            "error": "Source content is empty."
        }


    # ========================================================
    # INFOGRAPHIC
    # ========================================================

    if request.outputType == "Infographic":

        try:

            infographic = generate_infographic(
                source_content=request.sourceText,
                target_audience=request.audience,
                tone=request.tone,
                language="English",
                detail_level="Medium",
                communication_objective="Awareness",
            )

            return {
                "success": True,
                "outputType": "Infographic",
                "content": infographic,
                "file": None,
            }

        except Exception as exc:

            return {
                "success": False,
                "error": str(exc)
            }


    # ========================================================
    # VIDEO
    # ========================================================

    if request.outputType in [
        "Video",
        "Video Script"
    ]:

        try:

            result = generate_video(
                source_content=request.sourceText,
                target_audience=request.audience,
                tone=request.tone,
                duration=request.duration,
                language="English",
                detail_level="Medium",
                communication_objective="Inform",
            )


            # ------------------------------------------------
            # Generation failed
            # ------------------------------------------------

            if not result.get("success"):

                return {
                    "success": False,
                    "error": result.get(
                        "error",
                        "Video generation failed."
                    )
                }


            # ------------------------------------------------
            # Get generated video
            # ------------------------------------------------

            source_file = result.get("file")


            if not source_file:

                return {
                    "success": True,
                    "outputType": request.outputType,
                    "content": result.get("content"),
                    "file": None,
                    "warning": (
                        "Video generator completed "
                        "but did not return a file path."
                    )
                }


            # ------------------------------------------------
            # Convert path
            # ------------------------------------------------

            source_path = Path(source_file)


            if not source_path.is_absolute():

                source_path = BASE_DIR / source_path


            # ------------------------------------------------
            # Check file
            # ------------------------------------------------

            if not source_path.exists():

                return {
                    "success": False,
                    "error": (
                        f"Generated video was not found: "
                        f"{source_path}"
                    )
                }


            # ------------------------------------------------
            # Copy final video into public folder
            # ------------------------------------------------

            extension = source_path.suffix or ".mp4"

            target_path = (
                VIDEO_DIR /
                f"video_{uuid.uuid4().hex}{extension}"
            )


            target_path.write_bytes(
                source_path.read_bytes()
            )


            # ------------------------------------------------
            # Return browser URL
            # ------------------------------------------------

            return {
                "success": True,

                "outputType": request.outputType,

                "content": result.get("content"),

                "file": public_asset(
                    http_request,
                    "generated-video",
                    target_path
                )
            }


        except Exception as exc:

            return {
                "success": False,
                "error": str(exc)
            }


    # ========================================================
    # POWERPOINT
    # ========================================================

    if request.outputType in [
        "PowerPoint",
        "Presentation"
    ]:

        try:

            # ------------------------------------------------
            # Generate PPT plan
            # ------------------------------------------------

            result = generate_ppt_plan(

                source_content=request.sourceText,

                target_audience=request.audience,

                tone=request.tone,

                language="English",

                detail_level="Medium",

                communication_objective="Inform",

                content_style="Clear and Structured"
            )


            # ------------------------------------------------
            # Generator error
            # ------------------------------------------------

            if not result.get("success"):

                return {
                    "success": False,
                    "error": result.get(
                        "error",
                        "PPT generation failed."
                    )
                }


            # ------------------------------------------------
            # Get presentation JSON
            # ------------------------------------------------

            presentation = result.get(
                "presentation"
            )


            if not presentation:

                return {
                    "success": False,
                    "error": (
                        "PPT generator returned "
                        "no presentation."
                    )
                }


            # ------------------------------------------------
            # Generate unique filename
            # ------------------------------------------------

            filename = (
                f"presentation_"
                f"{uuid.uuid4().hex}.pptx"
            )


            output_path = (
                PPT_DIR / filename
            )


            # ------------------------------------------------
            # Render PPTX
            # ------------------------------------------------

            render_ppt(

                presentation_data=presentation,

                output_path=str(output_path)
            )


            # ------------------------------------------------
            # Verify file
            # ------------------------------------------------

            if not output_path.exists():

                return {
                    "success": False,
                    "error": (
                        "PPT renderer finished "
                        "but PPTX file was not created."
                    )
                }


            # ------------------------------------------------
            # Return public URL
            # ------------------------------------------------

            return {

                "success": True,

                "outputType": "PowerPoint",

                "content": presentation,

                "file": public_asset(

                    http_request,

                    "generated-ppt",

                    output_path
                )
            }


        except Exception as exc:

            return {
                "success": False,
                "error": str(exc)
            }


    # ========================================================
    # OTHER CONTENT TYPES
    # ========================================================

    output_type_map = {

        "Summary":
            "executive_summary",

        "Advisory":
            "advisory",

        "LinkedIn Post":
            "linkedin_post",

        "Twitter/X Post":
            "twitter_post",
    }


    generator_output_type = (
        output_type_map.get(
            request.outputType
        )
    )


    if not generator_output_type:

        return {
            "success": False,
            "error": (
                f"{request.outputType} "
                "generator is not connected yet."
            )
        }


    # ========================================================
    # CONTENT GENERATOR
    # ========================================================

    try:

        result = generate_content(

            source_content=request.sourceText,

            output_types=[
                generator_output_type
            ],

            target_audience=request.audience,

            tone=request.tone,
        )


        output = result.get(
            generator_output_type
        )


        if not output:

            return {
                "success": False,
                "error": (
                    "Generator returned no result."
                )
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

            "content": output["content"],

            "file": None
        }


    except Exception as exc:

        return {
            "success": False,
            "error": str(exc)
        }