# Frontend Documentation
## Overview
The frontend is built with **Next.js / React and TypeScript** and provides the user interface for the Content Transformer Platform.
The frontend allows users to enter source content, attach documents, select an output format, choose tone and audience, set video duration, send a request to the FastAPI backend, and view the generated result.
The main frontend page is:
```text
app/page.tsx
```
## Project Structure
```text
Frontend/
├── app/
│   └── page.tsx
├── components/
│   └── OutputWorkspace
└── lib/
    └── api
```
### Important Modules
**`page.tsx`**  
Main page containing the UI, state management, input handling, output selection, and API request logic.
**`@/lib/api`**  
Provides `transformContent()` and the `TransformResult` type for backend communication.
**`@/components/OutputWorkspace`**  
Displays the generated result returned by the backend.
**`lucide-react`**  
Provides the UI icons used throughout the page.
## Client-Side Rendering
The page starts with:
```text
"use client";
```
This enables React state, browser file selection, form controls, click handlers, and asynchronous API requests.
## State Management
The page uses React `useState` to manage:
| State | Purpose |
|---|---|
| `sourceText` | User-entered source text |
| `selectedFile` | Selected document |
| `outputType` | Selected deliverable type |
| `tone` | Communication tone |
| `audience` | Target audience |
| `duration` | Video duration in seconds |
| `result` | Backend transformation result |
| `loading` | Generation/loading state |
| `error` | Error message |
Default values are:
```text
Output Type : Summary
Tone        : Professional
Audience    : Executive Leadership
Duration    : 60 seconds
```
## Source Data Input
Users can provide source data in two ways.
### Text Input
A textarea accepts raw text, research summaries, intelligence reports, and press briefs. The page also displays the current character count.
### Document Upload
The file input accepts:
```text
.pdf
.doc
.docx
.txt
```
The selected filename is displayed and the user can clear the file before generation.
## Output Options
Supported deliverables are:
| Output Type | Description |
|---|---|
| Summary | Executive synthesis and key takeaways |
| Advisory | Threat assessment and policy brief |
| LinkedIn Post | Professional post and hashtags |
| Twitter/X Post | Thread and concise social updates |
| Presentation | Slide structure, bullets, and speaker notes |
| Infographic | Visual data breakdown and layout |
| Video | Generated video with workspace preview |
The selected output is stored in `outputType`.
## Communication Tone
Available options are:
```text
Professional
Urgent / Alert
Technical
Executive
```
The selected tone is sent to the backend.
## Target Audience
Available options are:
```text
Executive Leadership
Operators & Technical
Public Stakeholders
Analysts & Engineers
```
The selected audience is sent to the backend.
## Video Duration
The duration control is displayed only when:
```text
Output Type = Video
```
The allowed range is **10 to 600 seconds**. Presets are:
```text
30 sec | 60 sec | 90 sec | 2 min | 3 min | 5 min
```
The default duration is **60 seconds**.
## API Integration
The frontend uses:
```text
transformContent()
```
from:
```text
@/lib/api
```
The main backend endpoint is:
```text
POST /api/transform
```
Request structure:
```json
{
  "sourceText": "Your source content",
  "outputType": "Summary",
  "tone": "Professional",
  "audience": "Executive Leadership",
  "duration": 60
}
```
When a file is selected, the current page passes its name as:
```text
[File Attached: filename]
```
## Validation and Request Handling
The page requires at least one source:
```text
Source Text OR Selected File
```
When generation starts, the previous result and error are cleared and `loading` is enabled. The page then calls `transformContent()`.
If the response is unsuccessful, the returned error is stored in `error`. On success, the response is stored in `result`. The loading state is reset after the request completes.
## User Interface
The page is organized as:
```text
Navbar
  │
  ▼
Hero Section
  │
  ▼
Main Content
  ├── Source Data Input
  ├── Output Options
  ├── Tone / Audience
  ├── Video Duration
  └── Generate Deliverable
  │
  ▼
Output Workspace
  │
  ▼
Footer
```
Tailwind CSS classes are used for responsive layout, spacing, typography, borders, colors, and interactive states.
## Output Workspace
Generated results are passed to:
```text
<OutputWorkspace
  outputType={outputType}
  result={result}
/>
```
The workspace displays the generated content according to the selected output type. When a generated file is available, the UI shows an **Asset ready** status.
## Error and Loading States
During generation, the button displays a refresh/loading indicator and text such as:
```text
Generating Summary...
```
If an error occurs, the message is displayed in the frontend error area and the loading state is stopped.
## Basic Flow
```text
Frontend
   │
   ├── Enter Source Text / Attach File
   │
   ├── Select Output Type
   │
   ├── Select Tone & Audience
   │
   └── Set Video Duration
           │
           ▼
   Generate Deliverable
           │
           ▼
   transformContent()
           │
           ▼
   POST /api/transform
           │
           ▼
   FastAPI Backend
           │
           ▼
   JSON Transformation Result
           │
           ▼
   OutputWorkspace
           │
           ▼
   Display Generated Output
```
