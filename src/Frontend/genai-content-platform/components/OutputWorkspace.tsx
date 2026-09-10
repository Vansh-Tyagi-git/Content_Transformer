"use client";

import React, { useMemo, useRef, useState } from "react";

import {
  Download,
  FileText,
  Presentation,
  Brain,
  AlertTriangle,
  Network,
  ShieldCheck,
  ArrowRight,
  CheckCircle2,
  Target,
  Zap,
} from "lucide-react";

import html2canvas from "html2canvas";

import type { TransformResult } from "@/lib/api";

type Props = {
  outputType: string;
  result: TransformResult | null;
};

type InfographicData = {
  title?: string;
  subtitle?: string;
  key_message?: string;

  layout?: {
    type?: string;
    reason?: string;
  };

  key_statistics?: Array<{
    label?: string;
    value?: string | number;
  }>;

  sections?: Array<{
    section_title?: string;
    short_description?: string;
    key_points?: string[];
    visual_type?: string;
    visual_description?: string;
  }>;

  visual_hierarchy?: {
    primary_element?: string;
    secondary_elements?: string;
    supporting_elements?: string;
  };

  key_messaging?: {
    headline?: string;
    supporting_message?: string;
    call_to_action?: string;
  };

  design_recommendations?: {
    typography?: string;
    icon_usage?: string;
    chart_usage?: string;
    spacing?: string;
    information_density?: string;
  };

  fact_checking?: string[];
};

export default function OutputWorkspace({
  outputType,
  result,
}: Props) {
  const normalizedType = outputType.toLowerCase().trim();

  /* =========================================================
     EMPTY STATE
     ========================================================= */

  if (!result) {
    return (
      <div className="flex min-h-[520px] items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-white shadow-sm">
            <FileText className="h-7 w-7 text-slate-400" />
          </div>

          <h3 className="text-lg font-semibold text-slate-700">
            Your output will appear here
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Enter your content and choose an output format.
          </p>
        </div>
      </div>
    );
  }

  /* =========================================================
     INFOGRAPHIC
     ========================================================= */

  if (
    normalizedType === "infographic" ||
    normalizedType === "infographics"
  ) {
    return <InfographicCard result={result} />;
  }

  /* =========================================================
     PRESENTATION / POWERPOINT
     ========================================================= */

  if (
    normalizedType === "presentation" ||
    normalizedType === "powerpoint" ||
    normalizedType === "ppt"
  ) {
    return <PresentationWorkspace result={result} />;
  }

  /* =========================================================
     VIDEO
     ========================================================= */

  if (
    normalizedType === "video" ||
    normalizedType === "video script"
  ) {
    return <VideoWorkspace result={result} />;
  }

  /* =========================================================
     LINKEDIN
     ========================================================= */

  if (
    normalizedType === "linkedin" ||
    normalizedType === "linkedin post"
  ) {
    return <LinkedInWorkspace result={result} />;
  }

  /* =========================================================
     X / TWITTER
     ========================================================= */

  if (
    normalizedType === "twitter" ||
    normalizedType === "twitter/x post" ||
    normalizedType === "x post"
  ) {
    return <XWorkspace result={result} />;
  }

  /* =========================================================
     ADVISORY
     ========================================================= */

  if (normalizedType === "advisory") {
    return <AdvisoryWorkspace result={result} />;
  }

  /* =========================================================
     SUMMARY
     ========================================================= */

  if (normalizedType === "summary") {
    return <SummaryWorkspace result={result} />;
  }

  /* =========================================================
     FALLBACK
     ========================================================= */

  return <GenericWorkspace result={result} />;
}

/* ============================================================
   INFOGRAPHIC CARD
   ============================================================ */

function InfographicCard({
  result,
}: {
  result: TransformResult;
}) {
  const [activeSection, setActiveSection] = useState(0);
  const [downloading, setDownloading] = useState(false);

  /* ----------------------------------------------------------
     REF USED FOR PNG EXPORT
     ---------------------------------------------------------- */

  const infographicRef = useRef<HTMLDivElement>(null);

  const data = useMemo<InfographicData | null>(() => {
    try {
      if (!result.content) {
        return null;
      }

      if (typeof result.content === "object") {
        return result.content as InfographicData;
      }

      if (typeof result.content === "string") {
        return JSON.parse(result.content) as InfographicData;
      }

      return result.content as InfographicData;

    } catch {
      return null;
    }
  }, [result.content]);

  /* ----------------------------------------------------------
     DOWNLOAD INFOGRAPHIC AS PNG
     ---------------------------------------------------------- */

  const handleDownloadPNG = async () => {
    if (!infographicRef.current) {
      return;
    }

    try {
      setDownloading(true);

      const canvas = await html2canvas(
        infographicRef.current,
        {
          backgroundColor: "#ffffff",
          scale: 2,
          useCORS: true,
          logging: false,
        }
      );

      const image = canvas.toDataURL("image/png");

      const link = document.createElement("a");

      link.href = image;

      const fileName =
        data?.title
          ?.replace(/[^a-z0-9]/gi, "_")
          .replace(/_+/g, "_")
          .replace(/^_|_$/g, "")
          .toLowerCase() ||
        "content-transformer-infographic";

      link.download = `${fileName}.png`;

      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);
    } catch (error) {
      console.error(
        "Failed to download infographic:",
        error
      );
    } finally {
      setDownloading(false);
    }
  };

  if (!data) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6">
        <h3 className="font-semibold text-red-700">
          Unable to render infographic
        </h3>

        <p className="mt-2 text-sm text-red-600">
          The backend returned invalid infographic JSON.
        </p>

        <pre className="mt-4 max-h-80 overflow-auto rounded-xl bg-white p-4 text-xs text-slate-700">
          {String(result.content)}
        </pre>
      </div>
    );
  }

  const sections = data.sections ?? [];
  const currentSection = sections[activeSection];

  return (
    <div
      ref={infographicRef}
      className="h-full overflow-auto rounded-2xl border border-slate-200 bg-white shadow-xl"
    >
      {/* =====================================================
          HEADER
          ===================================================== */}

      <div className="relative overflow-hidden bg-slate-950 px-8 py-8 text-white">
        <div className="absolute right-[-60px] top-[-80px] h-56 w-56 rounded-full bg-blue-500/20 blur-3xl" />

        <div className="relative z-10">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-blue-400/30 bg-blue-400/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-blue-300">
            <Brain className="h-3.5 w-3.5" />
            AI Infographic
          </div>

          <h1 className="max-w-4xl text-3xl font-bold tracking-tight md:text-4xl">
            {data.title || "Untitled Infographic"}
          </h1>

          {data.subtitle && (
            <p className="mt-3 max-w-3xl text-base leading-7 text-slate-300">
              {data.subtitle}
            </p>
          )}
        </div>
      </div>

      {/* =====================================================
          KEY MESSAGE
          ===================================================== */}

      {data.key_message && (
        <div className="border-b border-slate-200 bg-slate-50 px-8 py-6">
          <div className="flex items-start gap-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-100">
              <Target className="h-5 w-5 text-blue-600" />
            </div>

            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-blue-600">
                Key Message
              </p>

              <p className="mt-1 text-lg font-semibold leading-7 text-slate-800">
                {data.key_message}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================
          SECTION NAVIGATION
          ===================================================== */}

      {sections.length > 0 && (
        <div className="border-b border-slate-200 bg-white px-8 py-4">
          <div className="flex gap-2 overflow-x-auto">
            {sections.map((section, index) => (
              <button
                key={index}
                onClick={() =>
                  setActiveSection(index)
                }
                className={`whitespace-nowrap rounded-xl px-4 py-2.5 text-sm font-semibold transition ${
                  activeSection === index
                    ? "bg-slate-900 text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {index + 1}.{" "}
                {section.section_title ||
                  `Section ${index + 1}`}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* =====================================================
          MAIN CONTENT
          ===================================================== */}

      <div className="p-8">
        {currentSection ? (
          <div className="grid gap-6 lg:grid-cols-[1fr_280px]">

            {/* LEFT */}

            <div>
              <div className="mb-6">
                <div className="mb-3 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100">
                    {getSectionIcon(
                      currentSection.visual_type
                    )}
                  </div>

                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Section {activeSection + 1}
                    </p>

                    <h2 className="text-2xl font-bold text-slate-900">
                      {currentSection.section_title}
                    </h2>
                  </div>
                </div>

                {currentSection.short_description && (
                  <p className="max-w-3xl text-sm leading-6 text-slate-500">
                    {currentSection.short_description}
                  </p>
                )}
              </div>

              {/* KEY POINT CARDS */}

              <div className="space-y-3">
                {(currentSection.key_points ?? []).map(
                  (point, index) => (
                    <div
                      key={index}
                      className="group flex items-start gap-4 rounded-xl border border-slate-200 bg-white p-4 transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md"
                    >
                      <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-xs font-bold text-slate-600 group-hover:bg-blue-100 group-hover:text-blue-600">
                        {index + 1}
                      </div>

                      <p className="text-sm font-medium leading-6 text-slate-700">
                        {point}
                      </p>

                      <CheckCircle2 className="ml-auto mt-1 h-4 w-4 shrink-0 text-slate-300 group-hover:text-blue-500" />
                    </div>
                  )
                )}
              </div>
            </div>

            {/* RIGHT VISUAL CARD */}

            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <p className="mb-4 text-xs font-bold uppercase tracking-wider text-slate-400">
                Visual Concept
              </p>

              <div className="flex min-h-[190px] flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white p-6 text-center">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50">
                  {getLargeSectionIcon(
                    currentSection.visual_type
                  )}
                </div>

                <p className="text-sm font-semibold text-slate-700">
                  {formatVisualType(
                    currentSection.visual_type
                  )}
                </p>

                {currentSection.visual_description && (
                  <p className="mt-2 text-xs leading-5 text-slate-500">
                    {currentSection.visual_description}
                  </p>
                )}
              </div>

              {/* PROGRESS */}

              <div className="mt-5">
                <div className="mb-2 flex justify-between text-xs text-slate-400">
                  <span>Progress</span>

                  <span>
                    {activeSection + 1} /{" "}
                    {sections.length}
                  </span>
                </div>

                <div className="h-2 overflow-hidden rounded-full bg-slate-200">
                  <div
                    className="h-full rounded-full bg-blue-600 transition-all"
                    style={{
                      width: `${
                        ((activeSection + 1) /
                          sections.length) *
                        100
                      }%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="py-12 text-center text-slate-500">
            No infographic sections available.
          </div>
        )}
      </div>

      {/* =====================================================
          KEY MESSAGING
          ===================================================== */}

      {data.key_messaging && (
        <div className="mx-8 mb-8 rounded-2xl bg-slate-900 p-6 text-white">
          <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/10">
              <Zap className="h-5 w-5 text-blue-300" />
            </div>

            <div className="flex-1">
              {data.key_messaging.headline && (
                <h3 className="text-xl font-bold">
                  {data.key_messaging.headline}
                </h3>
              )}

              {data.key_messaging.supporting_message && (
                <p className="mt-2 text-sm leading-6 text-slate-300">
                  {data.key_messaging.supporting_message}
                </p>
              )}

              {data.key_messaging.call_to_action && (
                <div className="mt-4 inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-semibold text-slate-900">
                  {data.key_messaging.call_to_action}
                  <ArrowRight className="h-4 w-4" />
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* =====================================================
          FOOTER
          ===================================================== */}

      <div className="flex flex-col gap-4 border-t border-slate-200 bg-white px-8 py-5 sm:flex-row sm:items-center sm:justify-between">
        <span className="text-xs text-slate-400">
          Generated by Content Transformer
        </span>

        <button
          type="button"
          onClick={handleDownloadPNG}
          disabled={downloading}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-xs font-bold text-white shadow-lg shadow-slate-200 transition-all hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-60"
        >
          <Download className="h-4 w-4" />

          {downloading
            ? "Preparing PNG..."
            : "Download PNG"}
        </button>
      </div>
    </div>
  );
}

/* ============================================================
   ICON HELPERS
   ============================================================ */

function getSectionIcon(type?: string) {
  const value = type?.toLowerCase() || "";

  if (value.includes("icon")) {
    return (
      <AlertTriangle className="h-5 w-5 text-amber-600" />
    );
  }

  if (value.includes("diagram")) {
    return (
      <Network className="h-5 w-5 text-blue-600" />
    );
  }

  if (value.includes("process")) {
    return (
      <ArrowRight className="h-5 w-5 text-green-600" />
    );
  }

  return (
    <Brain className="h-5 w-5 text-blue-600" />
  );
}

function getLargeSectionIcon(type?: string) {
  const value = type?.toLowerCase() || "";

  if (value.includes("icon")) {
    return (
      <AlertTriangle className="h-8 w-8 text-amber-600" />
    );
  }

  if (value.includes("diagram")) {
    return (
      <Network className="h-8 w-8 text-blue-600" />
    );
  }

  if (value.includes("process")) {
    return (
      <ArrowRight className="h-8 w-8 text-green-600" />
    );
  }

  return (
    <Brain className="h-8 w-8 text-blue-600" />
  );
}

function formatVisualType(type?: string) {
  if (!type) {
    return "Visual";
  }

  return type
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}

/* ============================================================
   PRESENTATION / PPT
   ============================================================ */

function PresentationWorkspace({
  result,
}: {
  result: TransformResult;
}) {
  const downloadUrl =
    result.file?.download_url || result.file?.url;

  return (
    <div className="flex min-h-[600px] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">

      {/* HEADER */}

      <div className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-orange-50">
            <Presentation className="h-5 w-5 text-orange-500" />
          </div>

          <div>
            <h2 className="text-lg font-bold text-slate-800">
              Presentation
            </h2>

            <p className="text-xs text-slate-400">
              PowerPoint presentation
            </p>
          </div>
        </div>
      </div>

      {/* SUCCESS AREA */}

      <div className="flex flex-1 flex-col items-center justify-center px-6 py-16 text-center">

        {/* LARGE GREEN TICK */}

        <div className="mb-8 flex h-32 w-32 items-center justify-center rounded-full bg-green-50 ring-8 ring-green-50/60">
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-green-500 shadow-xl shadow-green-200">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-14 w-14"
            >
              <path d="M20 6 9 17l-5-5" />
            </svg>
          </div>
        </div>

        {/* SUCCESS TITLE */}

        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          PPT Generated Successfully
        </h1>

        {/* DESCRIPTION */}

        <p className="mt-3 max-w-md text-sm leading-6 text-slate-500">
          Your PowerPoint presentation has been generated
          successfully and is ready to download.
        </p>

        {/* FILE CARD */}

        {result.file?.name && (
          <div className="mt-8 flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-orange-100">
              <Presentation className="h-5 w-5 text-orange-600" />
            </div>

            <div className="text-left">
              <p className="text-xs font-medium text-slate-400">
                Generated file
              </p>

              <p className="mt-0.5 max-w-[300px] truncate text-sm font-semibold text-slate-700">
                {result.file.name}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* BOTTOM DOWNLOAD */}

      <div className="border-t border-slate-200 bg-slate-50 px-6 py-5">
        {downloadUrl ? (
          <a
            href={downloadUrl}
            target="_blank"
            rel="noopener noreferrer"
            download
            className="flex w-full items-center justify-center gap-3 rounded-xl bg-slate-900 px-6 py-4 text-sm font-bold text-white shadow-lg shadow-slate-200 transition-all hover:-translate-y-0.5 hover:bg-slate-800 hover:shadow-xl"
          >
            <Download className="h-5 w-5" />
            Download PowerPoint
          </a>
        ) : (
          <div className="rounded-xl bg-red-50 px-4 py-3 text-center text-sm font-medium text-red-600">
            Download link is not available.
          </div>
        )}
      </div>
    </div>
  );
}

/* ============================================================
   VIDEO
   ============================================================ */

function VideoWorkspace({
  result,
}: {
  result: TransformResult;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-lg">
      {result.file?.url ? (
        <video
          controls
          className="w-full rounded-xl bg-black"
          src={result.file.url}
        />
      ) : (
        <div className="rounded-xl bg-slate-950 p-8 text-slate-200">
          <p className="mb-3 text-sm font-semibold">
            Video Script
          </p>

          <pre className="whitespace-pre-wrap text-sm leading-6">
            {String(result.content)}
          </pre>
        </div>
      )}

      {result.file?.download_url && (
        <a
          href={result.file.download_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white"
        >
          <Download className="h-4 w-4" />
          Download Video
        </a>
      )}
    </div>
  );
}

/* ============================================================
   LINKEDIN
   ============================================================ */

function LinkedInWorkspace({
  result,
}: {
  result: TransformResult;
}) {
  return (
    <div className="mx-auto max-w-2xl rounded-2xl border border-slate-200 bg-white shadow-lg">
      <div className="border-b border-slate-200 p-5">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-blue-600 font-bold text-white">
            CT
          </div>

          <div>
            <p className="font-bold text-slate-900">
              Content Transformer
            </p>

            <p className="text-xs text-slate-500">
              Professional content
            </p>
          </div>
        </div>
      </div>

      <div className="whitespace-pre-wrap p-6 text-sm leading-7 text-slate-700">
        {String(result.content)}
      </div>

      <div className="border-t border-slate-200 px-6 py-4 text-xs text-slate-400">
        Like · Comment · Repost · Send
      </div>
    </div>
  );
}

/* ============================================================
   X / TWITTER
   ============================================================ */

function XWorkspace({
  result,
}: {
  result: TransformResult;
}) {
  return (
    <div className="mx-auto max-w-xl rounded-2xl border border-slate-200 bg-white shadow-lg">
      <div className="p-5">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-black text-sm font-bold text-white">
            X
          </div>

          <div>
            <p className="font-bold text-slate-900">
              Content Transformer
            </p>

            <p className="text-xs text-slate-400">
              @contenttransformer
            </p>
          </div>
        </div>

        <p className="whitespace-pre-wrap text-[15px] leading-6 text-slate-800">
          {String(result.content)}
        </p>

        <div className="mt-6 flex justify-between text-xs text-slate-400">
          <span>Reply</span>
          <span>Repost</span>
          <span>Like</span>
          <span>Share</span>
        </div>
      </div>
    </div>
  );
}

/* ============================================================
   ADVISORY
   ============================================================ */

function AdvisoryWorkspace({
  result,
}: {
  result: TransformResult;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6 text-white shadow-xl">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-red-500/10">
          <ShieldCheck className="h-6 w-6 text-red-400" />
        </div>

        <div>
          <p className="text-xs uppercase tracking-widest text-slate-500">
            Security Advisory
          </p>

          <h2 className="text-xl font-bold">
            Advisory Report
          </h2>
        </div>
      </div>

      <div className="whitespace-pre-wrap rounded-xl border border-slate-800 bg-slate-900 p-5 text-sm leading-7 text-slate-300">
        {String(result.content)}
      </div>
    </div>
  );
}

/* ============================================================
   SUMMARY
   ============================================================ */

function SummaryWorkspace({
  result,
}: {
  result: TransformResult;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-100">
          <FileText className="h-5 w-5 text-blue-600" />
        </div>

        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-blue-600">
            Executive Summary
          </p>

          <h2 className="text-2xl font-bold text-slate-900">
            Summary
          </h2>
        </div>
      </div>

      <div className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
        {String(result.content)}
      </div>
    </div>
  );
}

/* ============================================================
   GENERIC FALLBACK
   ============================================================ */

function GenericWorkspace({
  result,
}: {
  result: TransformResult;
}) {
  const content =
    typeof result.content === "string"
      ? result.content
      : JSON.stringify(result.content, null, 2);

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-lg">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-semibold text-slate-900">
          Generated Output
        </h2>

        {result.file?.download_url && (
          <a
            href={result.file.download_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white"
          >
            <Download className="h-4 w-4" />
            Download
          </a>
        )}
      </div>

      <pre className="max-h-[600px] overflow-auto whitespace-pre-wrap rounded-xl bg-slate-50 p-5 text-sm leading-6 text-slate-700">
        {content}
      </pre>
    </div>
  );
}