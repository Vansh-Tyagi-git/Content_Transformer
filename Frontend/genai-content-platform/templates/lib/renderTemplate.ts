"use server";
import ejs from "ejs";
import path from "path";

export async function renderEJS(templateName: string, data: Record<string, any>): Promise<string> {
  const fileMapping: Record<string, string> = {
    "Advisory Document": "advisory",
    "Presentation": "presentation",
    "Video Package": "video",
    "Infographic": "infographic",
    "LinkedIn Post": "linkedin",
    "Twitter/X Thread": "twitter",
    "Executive Summary": "summary",
  };

  const fileName = fileMapping[templateName] || "advisory";
  const filePath = path.join(process.cwd(), "templates", `${fileName}.ejs`);
  
  const html = await ejs.renderFile(filePath, data);
  return html;
}