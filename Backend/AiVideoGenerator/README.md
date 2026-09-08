# AI Video Generator – Automated Content Transformation

## 1. Project Overview

This module converts an English PDF/document into a professional animated explainer video using Generative AI.

The complete workflow is automated:

PDF → Content Extraction → AI Storyboard → AI Narration → Animated Visual Scenes → Subtitles → Final MP4

The user does not need to manually write the video script or storyboard.

---

## 2. Key Features

- PDF content extraction using PyMuPDF
- AI-powered content understanding and storyboard generation
- Automatic narration using Edge TTS
- Multiple professional narrator voices with automatic voice rotation
- 1-minute, 2-minute and 3-minute video duration options
- Content-aware animated visual scenes
- Domain-specific visual themes
- Professional corporate presentation style
- Automatic subtitle generation in SRT and VTT formats
- Scene-wise video generation
- Final MP4 video generation
- Previous generated videos are preserved in separate output folders

---

## 3. Technology Stack

- Python 3.11
- Google Gemini API
- PyMuPDF
- Edge TTS
- Pillow
- OpenCV
- NumPy
- MoviePy
- FFmpeg

---

## 4. System Workflow

```text
                PDF / Document
                      |
                      v
             Text Extraction
                 PyMuPDF
                      |
                      v
              Gemini AI Analysis
                      |
                      v
             Storyboard Generation
                      |
                      v
          Scene + Narration Planning
                      |
              +-------+-------+
              |               |
              v               v
        Edge TTS Voice     Visual Renderer
              |               |
              v               v
          Audio Files      Animated Scenes
              |               |
              +-------+-------+
                      |
                      v
              Subtitle Creation
                      |
                      v
                Final MP4