"use client";

import React, { useState } from "react";
import { 
  Search, 
  Globe, 
  ChevronRight, 
  ChevronDown, 
  FileText, 
  Presentation as PresentationIcon, 
  Video, 
  Upload, 
  Sparkles, 
  RefreshCw, 
  Download,
  CheckCircle2,
  PieChart,
  ShieldAlert,
  Zap,
  Bot
} from "lucide-react";

// Safe SVG Icons for Social Platforms
const LinkedInIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.25V10.9H6.46M7.86 6.72a1.47 1.47 0 1 0 0 2.94 1.47 1.47 0 0 0 0-2.94Z" />
  </svg>
);

const TwitterIcon = ({ className }: { className?: string }) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);

export default function App() {
  const [sourceText, setSourceText] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [outputType, setOutputType] = useState("Summary");
  const [tone, setTone] = useState("Professional");
  const [audience, setAudience] = useState("Executive Leadership");
  const [previewHtml, setPreviewHtml] = useState("");
  const [loading, setLoading] = useState(false);

  // Output Deliverable Types
  const outputOptions = [
    { id: "summary", label: "Summary", icon: FileText, desc: "Concise executive synthesis & key takeaways" },
    { id: "advisory", label: "Advisory", icon: ShieldAlert, desc: "Structured threat assessment & policy brief" },
    { id: "linkedin", label: "LinkedIn Post", icon: LinkedInIcon, desc: "Professional long-form post & hashtags" },
    { id: "twitter", label: "Twitter/X Post", icon: TwitterIcon, desc: "Engaging thread & concise social updates" },
    { id: "presentation", label: "Presentation", icon: PresentationIcon, desc: "Slide structure, bullets & speaker notes" },
    { id: "infographic", label: "Infographic", icon: PieChart, desc: "Visual data breakdown & infographic layout" },
    { id: "video", label: "Video Script", icon: Video, desc: "Scene-by-scene storyboard & voiceover script" },
  ];

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleTransform = async () => {
    if (!sourceText.trim() && !selectedFile) return;
    setLoading(true);

    try {
      const res = await fetch("/api/transform", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sourceText: sourceText || `[File Attached: ${selectedFile?.name}]`,
          outputType,
          tone,
          audience,
        }),
      });

      const result = await res.json();
      if (result.success) {
        setPreviewHtml(result.html);
      }
    } catch (err) {
      console.error("Transformation Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-sky-500 selection:text-white">
      
      {/* Navbar */}
      <header className="sticky top-0 z-50 bg-white/95 border-b border-slate-200 shadow-sm px-6 lg:px-12 py-3.5 flex items-center justify-between backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="text-xl font-extrabold text-slate-950 flex items-center gap-1.5">
            CONTENT<span className="text-sky-600 font-extrabold">TRANSFORMER</span>
          </div>
          <div className="hidden md:block h-5 w-[1px] bg-slate-200 mx-2" />
          <span className="hidden md:block text-[11px] font-medium tracking-wide text-slate-600 uppercase">
            ENTERPRISE AUTOMATION • GenAI Platform
          </span>
        </div>

        <div className="hidden lg:flex items-center gap-7 text-[11px] font-bold uppercase tracking-wider text-slate-800">
          <span className="flex items-center gap-1 hover:text-sky-600 cursor-pointer">SOLUTIONS <ChevronDown className="w-3.5 h-3.5 text-slate-400" /></span>
          <span className="hover:text-sky-600 cursor-pointer">KNOWLEDGE HUB</span>
          <span className="hover:text-sky-600 cursor-pointer">TRAINING</span>
          <span className="hover:text-sky-600 cursor-pointer">COMPANY</span>
        </div>

        <div className="flex items-center gap-5">
          <Search className="w-4 h-4 text-slate-500 hover:text-sky-600 cursor-pointer" />
          <Globe className="w-4 h-4 text-slate-500 hover:text-sky-600 cursor-pointer" />
          
          <div className="flex items-center gap-2.5 bg-slate-100 border border-slate-200 rounded-full pl-4 pr-1 py-1">
            <span className="text-[11px] font-bold text-slate-800 uppercase tracking-wider">Contact</span>
            <button className="w-6 h-6 bg-sky-600 hover:bg-sky-500 text-white rounded-full flex items-center justify-center transition">
              <ChevronRight className="w-3.5 h-3.5 stroke-[3]" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section with Minimal Enterprise Editorial Background */}
      <section className="relative overflow-hidden min-h-[420px] bg-[#070d1a] text-white flex flex-col justify-center px-6 lg:px-16 py-16 border-b border-slate-800">
        
        {/* Abstract Editorial Data-Flow SVG Background */}
        <div className="absolute inset-0 pointer-events-none z-0">
          <svg 
            className="w-full h-full object-cover opacity-60" 
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 1920 1080" 
            preserveAspectRatio="xMidYMid slice"
          >
            <defs>
              <linearGradient id="flowCyan" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.05"/>
                <stop offset="50%" stopColor="#38bdf8" stopOpacity="0.4"/>
                <stop offset="100%" stopColor="#818cf8" stopOpacity="0.1"/>
              </linearGradient>

              <linearGradient id="flowPurple" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#818cf8" stopOpacity="0.05"/>
                <stop offset="50%" stopColor="#c084fc" stopOpacity="0.3"/>
                <stop offset="100%" stopColor="#38bdf8" stopOpacity="0.1"/>
              </linearGradient>

              <linearGradient id="cardFill" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#1e293b" stopOpacity="0.5"/>
                <stop offset="100%" stopColor="#0f172a" stopOpacity="0.3"/>
              </linearGradient>
            </defs>

            {/* Grid Mesh */}
            <g stroke="#1e293b" strokeWidth="0.5" opacity="0.3">
              <line x1="0" y1="200" x2="1920" y2="200"/>
              <line x1="0" y1="540" x2="1920" y2="540"/>
              <line x1="0" y1="880" x2="1920" y2="880"/>
              <line x1="400" y1="0" x2="400" y2="1080"/>
              <line x1="960" y1="0" x2="960" y2="1080"/>
              <line x1="1520" y1="0" x2="1520" y2="1080"/>
            </g>

            {/* Left Source Cards */}
            <g transform="translate(100, 220) rotate(-3)">
              <rect width="120" height="150" rx="6" fill="url(#cardFill)" stroke="#334155" strokeWidth="1"/>
              <line x1="16" y1="24" x2="70" y2="24" stroke="#94a3b8" strokeWidth="2" opacity="0.5"/>
              <line x1="16" y1="42" x2="100" y2="42" stroke="#475569" strokeWidth="1.5" opacity="0.4"/>
              <line x1="16" y1="56" x2="90" y2="56" stroke="#475569" strokeWidth="1.5" opacity="0.4"/>
            </g>

            <g transform="translate(70, 520) rotate(2)">
              <rect width="140" height="100" rx="6" fill="url(#cardFill)" stroke="#334155" strokeWidth="1"/>
              <rect x="12" y="12" width="116" height="50" rx="3" fill="#020617" opacity="0.5"/>
            </g>

            {/* Flow Pathways */}
            <path d="M 240 290 C 500 290, 680 500, 960 500" fill="none" stroke="url(#flowCyan)" strokeWidth="1.5"/>
            <path d="M 220 570 C 480 570, 680 540, 960 540" fill="none" stroke="url(#flowPurple)" strokeWidth="1.5"/>
            <path d="M 960 500 C 1240 500, 1420 270, 1680 270" fill="none" stroke="url(#flowCyan)" strokeWidth="1.5"/>
            <path d="M 960 540 C 1240 540, 1420 750, 1660 750" fill="none" stroke="url(#flowPurple)" strokeWidth="1.5"/>

            {/* Structured Transformation Hub */}
            <g transform="translate(960, 520)">
              <circle cx="0" cy="0" r="120" fill="none" stroke="#334155" strokeWidth="1" strokeDasharray="6 8"/>
              <polygon points="0,-60 45,-45 60,0 45,45 0,60 -45,45 -60,0 -45,-45" fill="#0f172a" stroke="#38bdf8" strokeWidth="1" opacity="0.8"/>
            </g>

            {/* Right Output Deliverable Cards */}
            <g transform="translate(1680, 200) rotate(2)">
              <rect width="140" height="95" rx="6" fill="url(#cardFill)" stroke="#38bdf8" strokeWidth="1" opacity="0.8"/>
              <rect x="0" y="0" width="140" height="3" fill="#38bdf8"/>
            </g>

            <g transform="translate(1660, 680) rotate(-2)">
              <rect width="140" height="95" rx="6" fill="url(#cardFill)" stroke="#818cf8" strokeWidth="1" opacity="0.8"/>
              <rect x="16" y="50" width="12" height="30" rx="1" fill="#38bdf8" opacity="0.6"/>
              <rect x="34" y="32" width="12" height="48" rx="1" fill="#818cf8" opacity="0.8"/>
            </g>
          </svg>
        </div>

        {/* Hero Content */}
        <div className="max-w-4xl relative z-10 mx-auto w-full text-center lg:text-left">
          <span className="text-xs font-bold uppercase tracking-widest text-sky-400 flex items-center justify-center lg:justify-start gap-2 mb-3">
            <Zap className="w-3.5 h-3.5 text-sky-400" /> MULTIMODAL INFORMATION SYSTEM
          </span>
          
          <h1 className="text-4xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Enterprise Content Transformation Platform
          </h1>
          
          <p className="text-base text-slate-300 font-normal leading-relaxed max-w-2xl mt-3">
            Ingest unstructured reports, intelligence briefs, transcripts, and data streams into a centralized processing pipeline to generate advisories, executive summaries, decks, and media assets.
          </p>
        </div>
      </section>

      {/* Main Workspace */}
      <main className="flex-1 max-w-[1700px] w-full mx-auto p-6 lg:p-12 grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        {/* Left Input & Selection Form */}
        <section className="lg:col-span-6 xl:col-span-5 flex flex-col gap-8">
          
          {/* Source Data Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xl shadow-slate-100 flex flex-col gap-5">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <FileText className="w-4 h-4 text-sky-600" /> 1. Source Data Input
              </label>
              <span className="text-[11px] text-slate-400">{sourceText.length} chars</span>
            </div>

            <textarea
              className="w-full h-36 bg-slate-50 border border-slate-200 focus:border-sky-500 rounded-xl p-4 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none transition resize-none"
              placeholder="Paste raw text, research summaries, intelligence reports, or press briefs here..."
              value={sourceText}
              onChange={(e) => setSourceText(e.target.value)}
            />

            <div className="border-t border-slate-200 pt-3">
              <label className="text-xs font-medium text-slate-600 block mb-2">Or Attach Document (PDF, DOCX, TXT)</label>
              <div className="flex items-center gap-3">
                <label className="flex-1 flex items-center justify-center gap-2 bg-slate-50 border border-dashed border-slate-300 hover:border-sky-500 rounded-xl py-3 px-5 cursor-pointer text-xs text-slate-500 hover:text-slate-700 transition">
                  <Upload className="w-4 h-4 text-sky-600" />
                  <span>{selectedFile ? selectedFile.name : "Attach Document"}</span>
                  <input type="file" accept=".pdf,.doc,.docx,.txt" className="hidden" onChange={handleFileUpload} />
                </label>
                {selectedFile && (
                  <button onClick={() => setSelectedFile(null)} className="text-xs text-red-500 hover:underline px-2">
                    Clear
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Deliverables Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xl shadow-slate-100 flex flex-col gap-6">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-3.5">
                2. Target Deliverable Format
              </label>

              <div className="grid grid-cols-2 gap-3">
                {outputOptions.map((item) => {
                  const Icon = item.icon;
                  const isSelected = outputType === item.label;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setOutputType(item.label)}
                      className={`p-3.5 rounded-xl border text-left transition flex flex-col justify-between gap-2.5 ${
                        isSelected
                          ? "bg-sky-50 border-sky-500 text-sky-950 shadow-sm"
                          : "bg-slate-50 border-slate-200 text-slate-600 hover:border-sky-300 hover:text-slate-800"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <Icon className={`w-4 h-4 ${isSelected ? "text-sky-600" : "text-slate-400"}`} />
                        {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" />}
                      </div>
                      <div>
                        <div className="text-xs font-bold">{item.label}</div>
                        <div className="text-[10px] text-slate-500 line-clamp-1 mt-0.5">{item.desc}</div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-200">
              <div>
                <label className="text-xs font-medium text-slate-600 block mb-1.5">Communication Tone</label>
                <select 
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-sky-500 cursor-pointer"
                  value={tone}
                  onChange={(e) => setTone(e.target.value)}
                >
                  <option value="Professional">Professional</option>
                  <option value="Urgent">Urgent / Alert</option>
                  <option value="Technical">Technical</option>
                  <option value="Executive">Executive</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-medium text-slate-600 block mb-1.5">Target Audience</label>
                <select 
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-sky-500 cursor-pointer"
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                >
                  <option value="Executive Leadership">Executive Leadership</option>
                  <option value="Operators">Operators & Technical</option>
                  <option value="Public">Public Stakeholders</option>
                  <option value="Analysts">Analysts & Engineers</option>
                </select>
              </div>
            </div>

            <button
              onClick={handleTransform}
              disabled={loading || (!sourceText.trim() && !selectedFile)}
              className="w-full py-3.5 bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs rounded-xl shadow-lg disabled:opacity-40 disabled:cursor-not-allowed transition flex items-center justify-center gap-2 mt-1 uppercase tracking-wider"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  Generating {outputType}...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Generate Deliverable
                </>
              )}
            </button>
          </div>
        </section>

        {/* Right Preview Output Panel */}
        <section className="lg:col-span-6 xl:col-span-7 flex flex-col bg-white border border-slate-200 rounded-2xl p-6 shadow-xl shadow-slate-100 min-h-[600px]">
          <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-200">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-sky-600"></span>
              <h2 className="text-sm font-semibold text-slate-950">
                OUTPUT WORKSPACE • <span className="text-sky-600 uppercase">{outputType}</span>
              </h2>
            </div>

            {previewHtml && (
              <button
                onClick={() => window.print()}
                className="px-3.5 py-1.5 bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold rounded-lg border border-slate-200 flex items-center gap-1.5 transition"
              >
                <Download className="w-3.5 h-3.5" /> EXPORT DELIVERABLE
              </button>
            )}
          </div>

          <div className="flex-1 bg-slate-50 border border-slate-200 rounded-xl overflow-hidden relative flex flex-col">
            {previewHtml ? (
              <iframe
                srcDoc={previewHtml}
                className="w-full flex-1 border-none bg-white"
                title="Dynamic Preview Output"
              />
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-8 text-center gap-3">
                <div className="p-4 rounded-full bg-slate-100 border border-slate-200 text-slate-400 shadow-inner">
                  <Bot className="w-9 h-9 text-sky-500/70" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-slate-700">Workspace Ready</h3>
                  <p className="text-xs text-slate-500 max-w-sm mt-1">
                    Select any output format on the left and click Generate to view the rendered deliverable asset.
                  </p>
                </div>
              </div>
            )}
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-white px-6 lg:px-12 py-8 mt-12 text-xs text-slate-500 flex flex-col md:flex-row justify-between items-center gap-4">
        <div>
          © 2026 Content Transformer Platform. All Rights Reserved.
        </div>
        <div className="flex gap-6">
          <span className="hover:text-sky-600 cursor-pointer">PRIVACY POLICY</span>
          <span className="hover:text-sky-600 cursor-pointer">TERMS OF SERVICE</span>
          <span className="hover:text-sky-600 cursor-pointer">SECURITY COMPLIANCE</span>
        </div>
      </footer>
    </div>
  );
}