import { NextResponse } from "next/server";
import { renderEJS } from "@/lib/renderTemplate";

export async function POST(req: Request) {
  try {
    const { sourceText, outputType, tone, audience } = await req.json();

    // Mock response simulating an AI structured extraction
    const mockData = {
      title: `${outputType} Output`,
      audience: audience || "General Stakeholders",
      tone: tone || "Professional",
      summary: sourceText || "No source content provided.",
      keyPoints: [
        "First key point extracted from source material.",
        "Second critical operational highlight.",
        "Actionable recommendation based on analysis."
      ]
    };

    // Render EJS HTML dynamically based on outputType
    const htmlOutput = await renderEJS(outputType, mockData);

    return NextResponse.json({ success: true, html: htmlOutput });
  } catch (error) {
    return NextResponse.json({ success: false, error: "Failed to render template" }, { status: 500 });
  }
}