# Content Transformer Platform

An AI-powered content transformation platform that converts source material into multiple professional deliverables such as summaries, advisories, social media posts, infographics, presentations, and videos.

## ✨ Features

* 📝 Executive summaries
* ⚠️ Advisory / threat assessments
* 💼 LinkedIn posts
* 🐦 Twitter/X threads and posts
* 📊 Infographics
* 📑 PowerPoint presentations
* 🎬 AI-generated videos and video scripts
* 📎 Document input support (`.pdf`, `.doc`, `.docx`, `.txt`)
* 🎯 Custom tone and target audience
* ⏱️ Configurable video duration
* 📱 Responsive web interface

## 🏗️ Architecture

```text
User
 │
 ▼
Next.js / React Frontend
 │
 │ POST /api/transform
 ▼
FastAPI Backend
 │
 ├── Text Generation ──────► HuggingFace
 ├── Infographic Generation ► InfoGraph
 ├── Presentation ─────────► PPT Generator + Renderer
 └── Video Generation ─────► AI Video Generator
 │
 ▼
Generated Content / Files
```

## 🛠️ Tech Stack

### Frontend

* **Next.js**
* **React**
* **TypeScript**
* **Tailwind CSS**
* **Lucide React** — UI icons

### Backend

* **Python**
* **FastAPI**
* **Uvicorn**
* **Hugging Face** — AI/content generation
* **python-pptx / PPT tooling** — PowerPoint generation
* **AI Video Generation pipeline**

### Communication

* **REST API**
* JSON-based request/response
* CORS-enabled frontend ↔ backend communication

## 📁 Project Structure

```text
.
├── docs/
│   ├── Backend.md
│   └── Frontend.md
├── src/
│   ├── Backend/
│   │   ├── AiVideoGenerator/
│   │   ├── HuggingFace/
│   │   ├── generated_ppt/
│   │   ├── generated_video/
│   │   └── main.py
│   │
│   └── Frontend/
│       ├── genai-content-platform/
│       └── package.json
│
├── submission/
│   ├── DEMO.md
│   └── PRESENTATION.md
│
├── requirements.txt
├── README.md
└── LICENSE
```

## 🔌 API

The main backend endpoint is:

```text
POST /api/transform
```

Example request:

```json
{
  "sourceText": "Your source content",
  "outputType": "Summary",
  "tone": "Professional",
  "audience": "Executive Leadership",
  "duration": 60
}
```

Supported output types:

```text
Summary
Advisory
LinkedIn Post
Twitter/X Post
Infographic
Video
Video Script
Presentation
PowerPoint
```

Generated PowerPoint and video assets are returned with accessible file URLs.

## 🚀 Running Locally

### Backend

```bash
cd src/Backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend

```bash
cd src/Frontend/genai-content-platform
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:3000
```

## 🔄 Basic Usage

1. Enter source text or attach a supported document.
2. Select the desired output format.
3. Choose the communication tone.
4. Select the target audience.
5. Set video duration when generating a video.
6. Click **Generate Deliverable**.
7. The frontend sends the request to the FastAPI backend.
8. The generated content or asset is displayed in the Output Workspace.

## 📚 Documentation

More detailed documentation is available in:

* `docs/Backend.md` — Backend architecture, APIs, generation pipeline, and deployment details.
* `docs/Frontend.md` — Frontend architecture, components, state management, and API integration.
* `submission/DEMO.md` — Demo information.
* `submission/PRESENTATION.md` — Project presentation.

## 🌐 Live Deployment

The application is deployed and available online:

**[Content Transformer](https://content-transformer-steel.vercel.app/)**

## 📄 License

See `LICENSE` for license information.