import React from "react";


type AnyObject = Record<string, any>;


/* ============================================================
   HELPERS
   ============================================================ */

function toArray(value: any): any[] {

  return Array.isArray(value)
    ? value
    : [];
}


function first(
  obj: AnyObject,
  keys: string[],
  fallback: any = undefined
) {

  for (const key of keys) {

    if (
      obj?.[key] !== undefined &&
      obj?.[key] !== null
    ) {

      return obj[key];
    }
  }


  return fallback;
}


/* ============================================================
   INFOGRAPHIC
   ============================================================ */

export default function InfographicRenderer(
  {
    data
  }: {
    data: any;
  }
) {


  /* ----------------------------------------------------------
     Convert JSON string → object
     ---------------------------------------------------------- */

  const root: AnyObject =

    typeof data === "string"

      ? (() => {

          try {

            return JSON.parse(data);

          } catch {

            return {
              title: "Infographic",
              summary: data
            };
          }

        })()

      : data || {};


  /* ----------------------------------------------------------
     Main fields
     ---------------------------------------------------------- */

  const title = first(

    root,

    [
      "title",
      "headline",
      "heading"
    ],

    "Infographic"
  );


  const subtitle = first(

    root,

    [
      "subtitle",
      "subheading",
      "description"
    ],

    ""
  );


  const metrics = toArray(

    first(

      root,

      [
        "metrics",
        "key_metrics",
        "statistics"
      ],

      []
    )
  );


  const sections = toArray(

    first(

      root,

      [
        "sections",
        "content",
        "blocks"
      ],

      []
    )
  );


  const chart = first(

    root,

    [
      "chart",
      "bar_chart",
      "data_visualization"
    ],

    null
  );


  const summary = first(

    root,

    [
      "summary",
      "executive_summary",
      "overview"
    ],

    ""
  );


  const bars = toArray(

    chart?.data ||
    chart?.values ||
    chart?.items
  );


  /* ==========================================================
     UI
     ========================================================== */

  return (

    <div className="min-h-full bg-slate-50 p-5 md:p-8">

      <div className="mx-auto max-w-5xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">


        {/* ----------------------------------------------------
            HEADER
            ---------------------------------------------------- */}

        <div className="border-b border-slate-200 bg-slate-950 p-7 text-white">

          <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-sky-400">

            Generated Infographic

          </div>


          <h1 className="text-2xl font-extrabold md:text-3xl">

            {title}

          </h1>


          {subtitle && (

            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">

              {subtitle}

            </p>

          )}

        </div>


        {/* ----------------------------------------------------
            METRICS
            ---------------------------------------------------- */}

        {metrics.length > 0 && (

          <div className="grid grid-cols-2 gap-3 p-5 md:grid-cols-4">

            {metrics.map(
              (
                metric,
                index
              ) => {

                const item =
                  typeof metric === "object"

                    ? metric

                    : {
                        value: metric
                      };


                return (

                  <div
                    key={index}
                    className="rounded-xl border border-slate-200 bg-slate-50 p-4"
                  >

                    <div className="text-2xl font-extrabold text-slate-950">

                      {first(
                        item,
                        [
                          "value",
                          "number",
                          "stat"
                        ],
                        "—"
                      )}

                    </div>


                    <div className="mt-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">

                      {first(
                        item,
                        [
                          "label",
                          "name",
                          "title"
                        ],
                        "Metric"
                      )}

                    </div>

                  </div>
                );
              }
            )}

          </div>
        )}


        {/* ----------------------------------------------------
            SUMMARY
            ---------------------------------------------------- */}

        {summary && (

          <div className="mx-5 mb-5 rounded-xl border border-sky-100 bg-sky-50 p-5 text-sm leading-6 text-slate-700">

            <div className="mb-1 text-[10px] font-bold uppercase tracking-widest text-sky-700">

              Key takeaway

            </div>


            {typeof summary === "string"

              ? summary

              : JSON.stringify(summary)

            }

          </div>
        )}


        {/* ----------------------------------------------------
            CHART
            ---------------------------------------------------- */}

        {bars.length > 0 && (

          <div className="mx-5 mb-5 rounded-xl border border-slate-200 p-5">

            <h2 className="mb-4 text-sm font-bold text-slate-900">

              {chart?.title ||
                "Data overview"}

            </h2>


            <div className="space-y-4">

              {bars.map(
                (
                  bar,
                  index
                ) => {

                  const item =

                    typeof bar === "object"

                      ? bar

                      : {
                          label: String(bar),
                          value: 0
                        };


                  const raw =

                    Number(

                      first(
                        item,
                        [
                          "value",
                          "score",
                          "percentage",
                          "amount"
                        ],
                        0
                      )

                    ) || 0;


                  const max = Math.max(

                    ...bars.map(

                      (x) =>

                        Number(

                          first(
                            x || {},
                            [
                              "value",
                              "score",
                              "percentage",
                              "amount"
                            ],
                            0
                          )

                        ) || 0

                    ),

                    1
                  );


                  const width = Math.max(

                    3,

                    Math.min(
                      100,
                      (raw / max) * 100
                    )
                  );


                  return (

                    <div key={index}>

                      <div className="mb-1 flex justify-between text-xs font-medium text-slate-600">

                        <span>

                          {first(
                            item,
                            [
                              "label",
                              "name",
                              "title"
                            ],
                            `Item ${index + 1}`
                          )}

                        </span>


                        <span>

                          {raw}

                        </span>

                      </div>


                      <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">

                        <div
                          className="h-full rounded-full bg-sky-500"
                          style={{
                            width: `${width}%`
                          }}
                        />

                      </div>

                    </div>

                  );
                }
              )}

            </div>

          </div>

        )}


        {/* ----------------------------------------------------
            SECTIONS
            ---------------------------------------------------- */}

        {sections.length > 0 && (

          <div className="grid gap-4 p-5 md:grid-cols-2">

            {sections.map(
              (
                section,
                index
              ) => {

                const item =

                  typeof section === "object"

                    ? section

                    : {
                        body: section
                      };


                const bullets =
                  toArray(

                    first(
                      item,
                      [
                        "bullets",
                        "points",
                        "items"
                      ],
                      []
                    )
                  );


                return (

                  <article
                    key={index}
                    className="rounded-xl border border-slate-200 p-5"
                  >

                    <h3 className="text-sm font-bold text-slate-900">

                      {first(
                        item,
                        [
                          "title",
                          "heading",
                          "name"
                        ],
                        `Section ${index + 1}`
                      )}

                    </h3>


                    {(
                      item.description ||
                      item.body ||
                      item.text
                    ) && (

                      <p className="mt-2 text-sm leading-6 text-slate-600">

                        {String(

                          first(
                            item,
                            [
                              "description",
                              "body",
                              "text"
                            ],
                            ""
                          )

                        )}

                      </p>

                    )}


                    {bullets.length > 0 && (

                      <ul className="mt-3 space-y-2 text-sm text-slate-600">

                        {bullets.map(
                          (
                            bullet,
                            i
                          ) => (

                            <li
                              key={i}
                              className="flex gap-2"
                            >

                              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-sky-500" />


                              <span>

                                {
                                  typeof bullet === "object"

                                    ? JSON.stringify(bullet)

                                    : String(bullet)
                                }

                              </span>

                            </li>

                          )
                        )}

                      </ul>

                    )}

                  </article>

                );

              }
            )}

          </div>

        )}

      </div>

    </div>
  );
}