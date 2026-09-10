  "use client";

  import React, { useState } from "react";

  import {
    transformContent,
    type TransformResult,
  } from "@/lib/api";

  import OutputWorkspace from "@/components/OutputWorkspace";

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
    CheckCircle2,
    PieChart,
    ShieldAlert,
    Zap,
  } from "lucide-react";

  /* ============================================================
    LINKEDIN ICON
    ============================================================ */

  const LinkedInIcon = ({
    className,
  }: {
    className?: string;
  }) => (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M19 3a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h14m-.5 15.5v-5.3a3.26 3.26 0 0 0-3.26-3.26c-.85 0-1.84.52-2.28 1.3v-1.11h-2.79v8.37h2.79v-4.93c0-.77.62-1.4 1.39-1.4a1.4 1.4 0 0 1 1.4 1.4v4.93h2.75M6.46 10.9v8.37H9.25V10.9H6.46M7.86 6.72a1.47 1.47 0 1 0 0 2.94 1.47 1.47 0 0 0 0-2.94Z" />
    </svg>
  );

  /* ============================================================
    TWITTER ICON
    ============================================================ */

  const TwitterIcon = ({
    className,
  }: {
    className?: string;
  }) => (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  );

  /* ============================================================
    APP
    ============================================================ */

  export default function App() {
    /* ----------------------------------------------------------
      STATE
      ---------------------------------------------------------- */

    const [sourceText, setSourceText] = useState("");

    const [selectedFile, setSelectedFile] =
      useState<File | null>(null);

    const [outputType, setOutputType] =
      useState("Summary");

    const [tone, setTone] =
      useState("Professional");

    const [audience, setAudience] =
      useState("Executive Leadership");

    /*
    * VIDEO DURATION
    *
    * Default duration is 60 seconds.
    * This value is only shown/used when Video is selected.
    */
    const [duration, setDuration] =
      useState(60);

    const [result, setResult] =
      useState<TransformResult | null>(null);

    const [loading, setLoading] =
      useState(false);

    const [error, setError] =
      useState("");

    /* ----------------------------------------------------------
      OUTPUT OPTIONS
      ---------------------------------------------------------- */

    const outputOptions = [
      {
        id: "summary",
        label: "Summary",
        icon: FileText,
        desc:
          "Concise executive synthesis & key takeaways",
      },
      {
        id: "advisory",
        label: "Advisory",
        icon: ShieldAlert,
        desc:
          "Structured threat assessment & policy brief",
      },
      {
        id: "linkedin",
        label: "LinkedIn Post",
        icon: LinkedInIcon,
        desc:
          "Professional long-form post & hashtags",
      },
      {
        id: "twitter",
        label: "Twitter/X Post",
        icon: TwitterIcon,
        desc:
          "Engaging thread & concise social updates",
      },
      {
        id: "presentation",
        label: "Presentation",
        icon: PresentationIcon,
        desc:
          "Slide structure, bullets & speaker notes",
      },
      {
        id: "infographic",
        label: "Infographic",
        icon: PieChart,
        desc:
          "Visual data breakdown & infographic layout",
      },
      {
        id: "video",
        label: "Video",
        icon: Video,
        desc:
          "Generated video with playable workspace preview",
      },
    ];

    /* ----------------------------------------------------------
      FILE SELECT
      ---------------------------------------------------------- */

    const handleFileUpload = (
      e: React.ChangeEvent<HTMLInputElement>
    ) => {
      if (e.target.files?.[0]) {
        setSelectedFile(e.target.files[0]);
      }
    };

    /* ----------------------------------------------------------
      TRANSFORM
      ---------------------------------------------------------- */

    const handleTransform = async () => {
      /* ------------------------------------------------------
        VALIDATION
        ------------------------------------------------------ */

      if (!sourceText.trim() && !selectedFile) {
        return;
      }

      setLoading(true);
      setError("");
      setResult(null);

      try {
        /* ----------------------------------------------------
          BACKEND REQUEST
          ---------------------------------------------------- */

        const response = await transformContent({
          sourceText:
            sourceText ||
            `[File Attached: ${selectedFile?.name}]`,

          outputType,

          tone,

          audience,

          /*
          * Duration is now controlled by the user.
          * For non-video outputs this value is harmless.
          */
          duration,
        });

        /* ----------------------------------------------------
          BACKEND ERROR
          ---------------------------------------------------- */

        if (!response.success) {
          setError(
            response.error ||
              "Generation failed."
          );

          return;
        }

        /* ----------------------------------------------------
          SAVE RESULT
          ---------------------------------------------------- */

        setResult(response);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Transformation failed."
        );
      } finally {
        setLoading(false);
      }
    };

    /* ==========================================================
      UI
      ========================================================== */

    return (
      <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">

        {/* ======================================================
            NAVBAR
            ====================================================== */}

        <header className="sticky top-0 z-50 bg-white/95 border-b border-slate-200 shadow-sm px-6 lg:px-12 py-3.5 flex items-center justify-between backdrop-blur-md">

          <div className="flex items-center gap-3">

            <div className="text-xl font-extrabold text-slate-950">
              CONTENT{" "}
              <span className="text-sky-600">
                TRANSFORMER
              </span>
            </div>

            <div className="hidden md:block h-5 w-px bg-slate-200 mx-2" />

            <span className="hidden md:block text-[11px] font-medium tracking-wide text-slate-600 uppercase">
              ENTERPRISE AUTOMATION • GenAI Platform
            </span>

          </div>

          <div className="hidden lg:flex items-center gap-7 text-[11px] font-bold uppercase tracking-wider text-slate-800">

            <span className="flex items-center gap-1 hover:text-sky-600 cursor-pointer">
              SOLUTIONS
              <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
            </span>

            <span className="hover:text-sky-600 cursor-pointer">
              KNOWLEDGE HUB
            </span>

            <span className="hover:text-sky-600 cursor-pointer">
              TRAINING
            </span>

            <span className="hover:text-sky-600 cursor-pointer">
              COMPANY
            </span>

          </div>

          <div className="flex items-center gap-5">

            <Search className="w-4 h-4 text-slate-500" />

            <Globe className="w-4 h-4 text-slate-500" />

            <div className="flex items-center gap-2.5 bg-slate-100 border border-slate-200 rounded-full pl-4 pr-1 py-1">

              <span className="text-[11px] font-bold text-slate-800 uppercase tracking-wider">
                Contact
              </span>

              <button className="w-6 h-6 bg-sky-600 text-white rounded-full flex items-center justify-center">
                <ChevronRight className="w-3.5 h-3.5 stroke-[3]" />
              </button>

            </div>

          </div>

        </header>

        {/* ======================================================
            HERO
            ====================================================== */}

        <section className="relative overflow-hidden min-h-[420px] bg-[#070d1a] text-white flex flex-col justify-center px-6 lg:px-16 py-16 border-b border-slate-800">

          <div className="absolute inset-0 pointer-events-none opacity-40">

            <div className="absolute inset-0 bg-[linear-gradient(rgba(30,41,59,.35)_1px,transparent_1px),linear-gradient(90deg,rgba(30,41,59,.35)_1px,transparent_1px)] bg-[size:80px_80px]" />

          </div>

          <div className="max-w-4xl relative z-10 mx-auto w-full text-center lg:text-left">

            <span className="text-xs font-bold uppercase tracking-widest text-sky-400 flex items-center justify-center lg:justify-start gap-2 mb-3">
              <Zap className="w-3.5 h-3.5" />
              MULTIMODAL INFORMATION SYSTEM
            </span>

            <h1 className="text-4xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
              Enterprise Content Transformation Platform
            </h1>

            <p className="text-base text-slate-300 leading-relaxed max-w-2xl mt-3">
              Ingest unstructured reports, intelligence briefs,
              transcripts, and data streams into a centralized
              processing pipeline to generate advisories,
              executive summaries, decks, and media assets.
            </p>

          </div>

        </section>

        {/* ======================================================
            MAIN
            ====================================================== */}

        <main className="flex-1 max-w-[1700px] w-full mx-auto p-6 lg:p-12 grid grid-cols-1 lg:grid-cols-12 gap-10">

          {/* ====================================================
              LEFT PANEL
              ==================================================== */}

          <section className="lg:col-span-6 xl:col-span-5 flex flex-col gap-8">

            {/* ==================================================
                SOURCE DATA
                ================================================== */}

            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xl shadow-slate-100 flex flex-col gap-5">

              <div className="flex items-center justify-between">

                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-sky-600" />
                  1. Source Data Input
                </label>

                <span className="text-[11px] text-slate-400">
                  {sourceText.length} chars
                </span>

              </div>

              <textarea
                className="w-full h-36 bg-slate-50 border border-slate-200 focus:border-sky-500 rounded-xl p-4 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none transition resize-none"
                placeholder="Paste raw text, research summaries, intelligence reports, or press briefs here..."
                value={sourceText}
                onChange={(e) =>
                  setSourceText(e.target.value)
                }
              />

              <div className="border-t border-slate-200 pt-3">

                <label className="text-xs font-medium text-slate-600 block mb-2">
                  Or Attach Document (PDF, DOCX, TXT)
                </label>

                <div className="flex items-center gap-3">

                  <label className="flex-1 flex items-center justify-center gap-2 bg-slate-50 border border-dashed border-slate-300 hover:border-sky-500 rounded-xl py-3 px-5 cursor-pointer text-xs text-slate-500">

                    <Upload className="w-4 h-4 text-sky-600" />

                    <span>
                      {selectedFile
                        ? selectedFile.name
                        : "Attach Document"}
                    </span>

                    <input
                      type="file"
                      accept=".pdf,.doc,.docx,.txt"
                      className="hidden"
                      onChange={handleFileUpload}
                    />

                  </label>

                  {selectedFile && (
                    <button
                      onClick={() =>
                        setSelectedFile(null)
                      }
                      className="text-xs text-red-500 hover:underline px-2"
                    >
                      Clear
                    </button>
                  )}

                </div>

              </div>

            </div>

            {/* ==================================================
                OUTPUT OPTIONS
                ================================================== */}

            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xl shadow-slate-100 flex flex-col gap-6">

              <div>

                <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-3.5">
                  2. Target Deliverable Format
                </label>

                <div className="grid grid-cols-2 gap-3">

                  {outputOptions.map((item) => {
                    const Icon = item.icon;

                    const isSelected =
                      outputType === item.label;

                    return (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() =>
                          setOutputType(item.label)
                        }
                        className={`p-3.5 rounded-xl border text-left transition flex flex-col justify-between gap-2.5 ${
                          isSelected
                            ? "bg-sky-50 border-sky-500 text-sky-950 shadow-sm"
                            : "bg-slate-50 border-slate-200 text-slate-600 hover:border-sky-300"
                        }`}
                      >

                        <div className="flex items-center justify-between">

                          <Icon
                            className={`w-4 h-4 ${
                              isSelected
                                ? "text-sky-600"
                                : "text-slate-400"
                            }`}
                          />

                          {isSelected && (
                            <CheckCircle2 className="w-3.5 h-3.5 text-sky-600" />
                          )}

                        </div>

                        <div>

                          <div className="text-xs font-bold">
                            {item.label}
                          </div>

                          <div className="text-[10px] text-slate-500 line-clamp-1 mt-0.5">
                            {item.desc}
                          </div>

                        </div>

                      </button>
                    );
                  })}

                </div>

              </div>

              {/* =================================================
                  TONE / AUDIENCE
                  ================================================= */}

              <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-200">

                <div>

                  <label className="text-xs font-medium text-slate-600 block mb-1.5">
                    Communication Tone
                  </label>

                  <select
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-sky-500"
                    value={tone}
                    onChange={(e) =>
                      setTone(e.target.value)
                    }
                  >

                    <option value="Professional">
                      Professional
                    </option>

                    <option value="Urgent">
                      Urgent / Alert
                    </option>

                    <option value="Technical">
                      Technical
                    </option>

                    <option value="Executive">
                      Executive
                    </option>

                  </select>

                </div>

                <div>

                  <label className="text-xs font-medium text-slate-600 block mb-1.5">
                    Target Audience
                  </label>

                  <select
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs text-slate-800 focus:outline-none focus:border-sky-500"
                    value={audience}
                    onChange={(e) =>
                      setAudience(e.target.value)
                    }
                  >

                    <option value="Executive Leadership">
                      Executive Leadership
                    </option>

                    <option value="Operators">
                      Operators & Technical
                    </option>

                    <option value="Public">
                      Public Stakeholders
                    </option>

                    <option value="Analysts">
                      Analysts & Engineers
                    </option>

                  </select>

                </div>

              </div>

              {/* =================================================
                  VIDEO DURATION
                  ONLY VISIBLE FOR VIDEO
                  ================================================= */}

              {outputType === "Video" && (
                <div className="border-t border-slate-200 pt-4">

                  <label className="text-xs font-medium text-slate-600 block mb-1.5">
                    Video Duration
                  </label>

                  <div className="flex items-center gap-3">

                    <div className="relative flex-1">

                      <input
                        type="number"
                        min={10}
                        max={600}
                        step={5}
                        value={duration}
                        onChange={(e) =>
                          setDuration(
                            Math.max(
                              10,
                              Math.min(
                                600,
                                Number(e.target.value) || 10
                              )
                            )
                          )
                        }
                        className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 pr-16 text-sm text-slate-800 focus:outline-none focus:border-sky-500"
                      />

                      <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-slate-400">
                        seconds
                      </span>

                    </div>

                    <select
                      value={duration}
                      onChange={(e) =>
                        setDuration(
                          Number(e.target.value)
                        )
                      }
                      className="bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs text-slate-700 focus:outline-none focus:border-sky-500"
                    >

                      <option value={30}>
                        30 sec
                      </option>

                      <option value={60}>
                        60 sec
                      </option>

                      <option value={90}>
                        90 sec
                      </option>

                      <option value={120}>
                        2 min
                      </option>

                      <option value={180}>
                        3 min
                      </option>

                      <option value={300}>
                        5 min
                      </option>

                    </select>

                  </div>

                  <p className="mt-1.5 text-[10px] text-slate-400">
                    Choose between 10 seconds and 10 minutes.
                  </p>

                </div>
              )}

              {/* =================================================
                  ERROR
                  ================================================= */}

              {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-700">
                  {error}
                </div>
              )}

              {/* =================================================
                  GENERATE BUTTON
                  ================================================= */}

              <button
                onClick={handleTransform}
                disabled={
                  loading ||
                  (!sourceText.trim() &&
                    !selectedFile)
                }
                className="w-full py-3.5 bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs rounded-xl shadow-lg disabled:opacity-40 disabled:cursor-not-allowed transition flex items-center justify-center gap-2 uppercase tracking-wider"
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

          {/* ====================================================
              RIGHT WORKSPACE
              ==================================================== */}

          <section className="lg:col-span-6 xl:col-span-7 flex flex-col bg-white border border-slate-200 rounded-2xl p-6 shadow-xl shadow-slate-100 min-h-[600px]">

            {/* ==================================================
                WORKSPACE HEADER
                ================================================== */}

            <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-200">

              <div className="flex items-center gap-2">

                <span className="w-2.5 h-2.5 rounded-full bg-sky-600" />

                <h2 className="text-sm font-semibold text-slate-950">

                  OUTPUT WORKSPACE •{" "}

                  <span className="text-sky-600 uppercase">
                    {outputType}
                  </span>

                </h2>

              </div>

              {result?.file && (
                <span className="text-[10px] font-bold text-emerald-600 uppercase">
                  Asset ready
                </span>
              )}

            </div>

            {/* ==================================================
                WORKSPACE CONTENT
                ================================================== */}

            <div className="flex-1 bg-slate-50 border border-slate-200 rounded-xl overflow-hidden relative">

              <OutputWorkspace
                outputType={outputType}
                result={result}
              />

            </div>

          </section>

        </main>

        {/* ======================================================
            FOOTER
            ====================================================== */}

        <footer className="border-t border-slate-200 bg-white px-6 lg:px-12 py-8 mt-12 text-xs text-slate-500 flex flex-col md:flex-row justify-between items-center gap-4">

          <div>
            © 2026 Content Transformer Platform. All Rights Reserved.
          </div>

          <div className="flex gap-6">

            <span>
              PRIVACY POLICY
            </span>

            <span>
              TERMS OF SERVICE
            </span>

            <span>
              SECURITY COMPLIANCE
            </span>

          </div>

        </footer>

      </div>
    );
  }