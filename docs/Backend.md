# Backend Documentation

## Overview

The backend is built with **FastAPI** and provides APIs for transforming source content into different formats such as:

* Summary
* Advisory
* LinkedIn Post
* Twitter/X Post
* Infographic
* Video / Video Script
* PowerPoint Presentation

The main API entry point is:

```text
main.py
```

---

## Project Structure

```text
Backend/
├── main.py
├── requirements.tx
│
├── AiVideoGenerator/
│   ├── main.py
│   ├── generate_video.py
│   ├── audio/
│   ├── images/
│   ├── scenes/
│   └── outputs/
│
├── HuggingFace/
│   ├── content_generator.py
│   ├── InfoGraph.py
│   └── ppt/
│       ├── ppt_generator.py
│       └── ppt_renderer.py
│
├── generated_ppt/
└── generated_video/
```

### Important Modules

**`main.py`**
Main FastAPI application and API endpoints.

**`HuggingFace/content_generator.py`**
Generates text-based content such as summaries, advisories, LinkedIn posts, and Twitter/X posts.

**`HuggingFace/InfoGraph.py`**
Generates infographic content.

**`HuggingFace/ppt/ppt_generator.py`**
Creates the PowerPoint presentation structure/plan.

**`HuggingFace/ppt/ppt_renderer.py`**
Converts the generated presentation data into a `.pptx` file.

**`AiVideoGenerator/main.py`**
Generates videos and returns the generated video information.

**`generated_ppt/` and `generated_video/`**
Public directories where generated files are copied and served.

---

## API Endpoints

### `GET /`

Checks whether the backend is running.

```json
{
  "success": true,
  "message": "Backend is running"
}
```

### `GET /api/test`

Basic API connectivity test.

### `GET /api/confirm`

Used to confirm that the frontend can communicate with the FastAPI backend.

### `POST /api/transform`

Main endpoint of the application.

Request:

```json
{
  "sourceText": "Your source content",
  "outputType": "Summary",
  "tone": "Professional",
  "audience": "Executive Leadership",
  "duration": 60
}
```

`duration` is mainly used for video generation.

---

## Supported Output Types

| Output Type    | Backend Generator                      |
| -------------- | -------------------------------------- |
| Summary        | `generate_content()`                   |
| Advisory       | `generate_content()`                   |
| LinkedIn Post  | `generate_content()`                   |
| Twitter/X Post | `generate_content()`                   |
| Infographic    | `generate_infographic()`               |
| Video          | `generate_video()`                     |
| Video Script   | `generate_video()`                     |
| PowerPoint     | `generate_ppt_plan()` + `render_ppt()` |
| Presentation   | `generate_ppt_plan()` + `render_ppt()` |

---

## Generated Files

Generated PowerPoint files are served through:

```text
/generated-ppt/<filename>.pptx
```

Generated video files are served through:

```text
/generated-video/<filename>.mp4
```

The backend generates unique filenames using UUIDs to avoid overwriting previous files.

---

## CORS

The backend allows requests from the local frontend and configured Vercel frontend domains.

When deploying the frontend to a new domain, the domain should be added to the `allow_origins` list in `main.py`.

---

## Running the Backend

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Basic Flow

```text
Frontend
   │
   ▼
POST /api/transform
   │
   ├── Text Content ──► content_generator.py
   │
   ├── Infographic ──► InfoGraph.py
   │
   ├── Video ────────► AiVideoGenerator
   │
   └── PowerPoint ───► ppt_generator.py
                            │
                            ▼
                       ppt_renderer.py
   │
   ▼
Generated Output
```

The backend returns a JSON response containing the generated `content` and, for files such as videos and PowerPoint presentations, a publicly accessible `file` object containing the download/preview URL.
