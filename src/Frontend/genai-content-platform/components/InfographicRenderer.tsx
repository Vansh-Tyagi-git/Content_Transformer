"use client";

import React from "react";

import {
  BarChart3,
  TrendingUp,
  Target,
  Activity,
} from "lucide-react";

type AnyObject = Record<string, any>;

function toArray(value: any): any[] {
  return Array.isArray(value) ? value : [];
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

export default function InfographicRenderer({
  data,
}: {
  data: any;
}) {
  const root: AnyObject =
    typeof data === "string"
      ? (() => {
          try {
            return JSON.parse(data);
          } catch {
            return {
              title: "Generated Infographic",
              summary: data,
            };
          }
        })()
      : data || {};

  const title = first(
    root,
    ["title", "headline", "heading"],
    "Generated Infographic"
  );

  const subtitle = first(
    root,
    ["subtitle", "subheading", "description"],
    ""
  );

  const metrics = toArray(
    first(
      root,
      ["metrics", "key_metrics", "statistics"],
      []
    )
  );

  const sections = toArray(
    first(
      root,
      ["sections", "content", "blocks"],
      []
    )
  );

  const chart = first(
    root,
    ["chart", "bar_chart", "data_visualization"],
    null
  );

  const bars = toArray(
    chart?.data ||
      chart?.values ||
      chart?.items
  );

  const summary = first(
    root,
    ["summary", "executive_summary", "overview"],
    ""
  );

  const max = Math.max(
    ...bars.map((bar) =>
      Number(
        first(
          bar || {},
          [
            "value",
            "score",
            "percentage",
            "amount",
          ],
          0
        )
      ) || 0
    ),
    1
  );

  return (
    <div className="h-full min-h-[560px] overflow-y-auto bg-slate-100 p-5 md:p-8">

      <div className="mx-auto max-w-5xl overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-lg">

        {/* ====================================================
            HERO
           ==================================================== */}

        <div className="relative overflow-hidden bg-slate-950 px-7 py-9 text-white md:px-10">

          <div className="absolute right-0 top-0 h-64 w-64 rounded-full bg-sky-500/10 blur-3xl" />

          <div className="relative">

            <div className="mb-3 flex items-center gap-2 text-[10px] font-bold uppercase tracking-[0.25em] text-sky-400">
              <Activity className="h-3.5 w-3.5" />
              Data Intelligence
            </div>

            <h1 className="max-w-3xl text-3xl font-black leading-tight md:text-4xl">
              {title}
            </h1>

            {subtitle && (
              <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
                {subtitle}
              </p>
            )}
          </div>
        </div>

        {/* ====================================================
            METRICS
           ==================================================== */}

        {metrics.length > 0 && (
          <div className="grid grid-cols-2 border-b border-slate-200 md:grid-cols-4">

            {metrics.map((metric, index) => {
              const item =
                typeof metric === "object"
                  ? metric
                  : { value: metric };

              return (
                <div
                  key={index}
                  className="border-r border-slate-200 p-5 last:border-r-0"
                >
                  <div className="mb-3 flex h-8 w-8 items-center justify-center rounded-lg bg-sky-50">
                    <TrendingUp className="h-4 w-4 text-sky-600" />
                  </div>

                  <div className="text-2xl font-black text-slate-950">
                    {first(
                      item,
                      ["value", "number", "stat"],
                      "—"
                    )}
                  </div>

                  <div className="mt-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">
                    {first(
                      item,
                      ["label", "name", "title"],
                      "Metric"
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ====================================================
            SUMMARY
           ==================================================== */}

        {summary && (
          <div className="border-b border-slate-200 bg-sky-50 px-7 py-6 md:px-10">

            <div className="mb-2 flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-sky-700">
              <Target className="h-3.5 w-3.5" />
              Key Insight
            </div>

            <p className="max-w-4xl text-sm font-medium leading-7 text-slate-700">
              {typeof summary === "string"
                ? summary
                : JSON.stringify(summary)}
            </p>
          </div>
        )}

        {/* ====================================================
            CHART
           ==================================================== */}

        {bars.length > 0 && (
          <div className="border-b border-slate-200 p-7 md:p-10">

            <div className="mb-6 flex items-center justify-between">

              <div>
                <div className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
                  Data Visualization
                </div>

                <h2 className="mt-1 text-lg font-extrabold text-slate-950">
                  {chart?.title || "Data Overview"}
                </h2>
              </div>

              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100">
                <BarChart3 className="h-4 w-4 text-slate-600" />
              </div>
            </div>

            <div className="space-y-5">

              {bars.map((bar, index) => {
                const item =
                  typeof bar === "object"
                    ? bar
                    : {
                        label: String(bar),
                        value: 0,
                      };

                const raw =
                  Number(
                    first(
                      item,
                      [
                        "value",
                        "score",
                        "percentage",
                        "amount",
                      ],
                      0
                    )
                  ) || 0;

                const width = Math.max(
                  3,
                  Math.min(
                    100,
                    (raw / max) * 100
                  )
                );

                return (
                  <div key={index}>

                    <div className="mb-2 flex items-center justify-between text-xs">
                      <span className="font-semibold text-slate-700">
                        {first(
                          item,
                          [
                            "label",
                            "name",
                            "title",
                          ],
                          `Item ${index + 1}`
                        )}
                      </span>

                      <span className="font-bold text-slate-900">
                        {raw}
                      </span>
                    </div>

                    <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-sky-500 transition-all"
                        style={{
                          width: `${width}%`,
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* ====================================================
            SECTIONS
           ==================================================== */}

        {sections.length > 0 && (
          <div className="grid gap-4 p-7 md:grid-cols-2 md:p-10">

            {sections.map((section, index) => {
              const item =
                typeof section === "object"
                  ? section
                  : { body: section };

              const bullets = toArray(
                first(
                  item,
                  [
                    "bullets",
                    "points",
                    "items",
                  ],
                  []
                )
              );

              return (
                <article
                  key={index}
                  className="rounded-2xl border border-slate-200 bg-slate-50 p-5"
                >
                  <div className="mb-3 flex items-center gap-2">

                    <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-white shadow-sm">
                      <span className="text-[10px] font-black text-sky-600">
                        {String(index + 1).padStart(
                          2,
                          "0"
                        )}
                      </span>
                    </div>

                    <h3 className="text-sm font-bold text-slate-900">
                      {first(
                        item,
                        [
                          "title",
                          "heading",
                          "name",
                        ],
                        `Section ${index + 1}`
                      )}
                    </h3>
                  </div>

                  {first(item, [
                    "description",
                    "body",
                    "text",
                  ]) && (
                    <p className="text-xs leading-6 text-slate-600">
                      {String(
                        first(item, [
                          "description",
                          "body",
                          "text",
                        ])
                      )}
                    </p>
                  )}

                  {bullets.length > 0 && (
                    <ul className="mt-4 space-y-2">
                      {bullets.map(
                        (bullet, i) => (
                          <li
                            key={i}
                            className="flex gap-2 text-xs leading-5 text-slate-600"
                          >
                            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-sky-500" />

                            {typeof bullet ===
                            "object"
                              ? JSON.stringify(
                                  bullet
                                )
                              : String(
                                  bullet
                                )}
                          </li>
                        )
                      )}
                    </ul>
                  )}
                </article>
              );
            })}
          </div>
        )}

        {/* ====================================================
            FOOTER
           ==================================================== */}

        <div className="border-t border-slate-200 bg-slate-50 px-7 py-4 text-center text-[9px] font-bold uppercase tracking-[0.2em] text-slate-400">
          Content Transformer • Generated Intelligence Asset
        </div>
      </div>
    </div>
  );
}