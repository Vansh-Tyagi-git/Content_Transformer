import React from "react";

import {
  Download,
  FileText,
  Presentation,
  ExternalLink
} from "lucide-react";

import type {
  TransformResult
} from "@/lib/api";

import InfographicRenderer
  from "./InfographicRenderer";


/* ============================================================
   HTML ESCAPE
   ============================================================ */

function escapeHtml(
  value: string
) {

  return value

    .replace(
      /&/g,
      "&amp;"
    )

    .replace(
      /</g,
      "&lt;"
    )

    .replace(
      />/g,
      "&gt;"
    )

    .replace(
      /"/g,
      "&quot;"
    )

    .replace(
      /'/g,
      "&#039;"
    );
}


/* ============================================================
   TEXT → HTML
   ============================================================ */

function textToHtml(
  value: string
) {

  const safe =
    escapeHtml(value);


  return `

<!doctype html>

<html>

<head>

<meta charset="utf-8">

<style>

body {

  font-family: Arial, sans-serif;

  margin: 0;

  padding: 32px;

  color: #0f172a;

  line-height: 1.7;

  background: #ffffff;

}

pre {

  white-space: pre-wrap;

  word-wrap: break-word;

  font-family: Arial, sans-serif;

}

h1,
h2,
h3 {

  color: #0f172a;

}

</style>

</head>

<body>

<pre>${safe}</pre>

</body>

</html>

`;
}


/* ============================================================
   OUTPUT WORKSPACE
   ============================================================ */

export default function OutputWorkspace({

  outputType,

  result,

}: {

  outputType: string;

  result: TransformResult | null;

}) {


  /* ==========================================================
     EMPTY STATE
     ========================================================== */

  if (!result) {

    return (

      <div className="flex h-full min-h-[500px] flex-col items-center justify-center p-8 text-center">

        <div className="rounded-full border border-slate-200 bg-slate-100 p-4">

          <FileText className="h-9 w-9 text-sky-500/70" />

        </div>


        <h3 className="mt-4 text-sm font-medium text-slate-700">

          Workspace Ready

        </h3>


        <p className="mt-1 max-w-sm text-xs text-slate-500">

          Select an output format and click Generate to view the result here.

        </p>

      </div>

    );
  }


  /* ==========================================================
     INFOGRAPHIC
     ========================================================== */

  if (
    outputType === "Infographic"
  ) {

    return (

      <InfographicRenderer
        data={result.content}
      />

    );
  }


  /* ==========================================================
     VIDEO
     ========================================================== */

  if (

    result.file?.url &&

    (
      outputType === "Video" ||
      outputType === "Video Script"
    )

  ) {

    return (

      <div className="flex h-full min-h-[500px] flex-col bg-slate-950">


        <video

          className="h-full min-h-[500px] w-full object-contain"

          controls

          playsInline

          src={result.file.url}

        />


        <div className="flex items-center justify-between border-t border-slate-800 bg-white p-3">


          <span className="text-xs text-slate-600">

            {result.file.name}

          </span>


          <a

            href={
              result.file.download_url
            }

            download

            className="flex items-center gap-2 rounded-lg bg-sky-600 px-3 py-2 text-xs font-bold text-white"

          >

            <Download className="h-3.5 w-3.5" />

            Download video

          </a>

        </div>

      </div>

    );
  }


  /* ==========================================================
     POWERPOINT
     ========================================================== */

  if (

    result.file?.url &&

    (
      outputType === "Presentation" ||
      outputType === "PowerPoint"
    )

  ) {

    const officePreview =

      `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(
        result.file.url
      )}`;


    return (

      <div className="flex h-full min-h-[500px] flex-col bg-slate-100">


        {/* ----------------------------------------------------
            POWERPOINT PREVIEW
            ---------------------------------------------------- */}

        <iframe

          src={officePreview}

          title="PowerPoint preview"

          className="min-h-[500px] flex-1 border-0 bg-white"

        />


        {/* ----------------------------------------------------
            CONTROLS
            ---------------------------------------------------- */}

        <div className="flex items-center justify-between border-t border-slate-200 bg-white p-3">


          <div className="flex items-center gap-2 text-xs text-slate-600">

            <Presentation className="h-4 w-4 text-sky-600" />

            {result.file.name}

          </div>


          <div className="flex gap-2">


            <a

              href={officePreview}

              target="_blank"

              rel="noreferrer"

              className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700"

            >

              <ExternalLink className="h-3.5 w-3.5" />

              Open preview

            </a>


            <a

              href={
                result.file.download_url
              }

              download

              className="flex items-center gap-2 rounded-lg bg-sky-600 px-3 py-2 text-xs font-bold text-white"

            >

              <Download className="h-3.5 w-3.5" />

              Download PPTX

            </a>


          </div>

        </div>

      </div>

    );
  }


  /* ==========================================================
     NORMAL STRING CONTENT
     ========================================================== */

  if (
    typeof result.content ===
    "string"
  ) {

    const looksLikeHtml =

      /<([a-z][\s\S]*?)>/i.test(
        result.content
      );


    return (

      <iframe

        srcDoc={

          looksLikeHtml

            ? result.content

            : textToHtml(
                result.content
              )

        }

        title="Generated content"

        className="h-full min-h-[500px] w-full border-0 bg-white"

      />

    );
  }


  /* ==========================================================
     FALLBACK JSON
     ========================================================== */

  return (

    <iframe

      srcDoc={textToHtml(

        JSON.stringify(
          result.content,
          null,
          2
        )

      )}

      title="Generated JSON"

      className="h-full min-h-[500px] w-full border-0 bg-white"

    />

  );
}