const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";


/* ============================================================
   FILE ASSET
   ============================================================ */

export type FileAsset = {

  name: string;

  url: string;

  download_url: string;

  preview_url?: string | null;

  media_type: string;
};


/* ============================================================
   TRANSFORM RESULT
   ============================================================ */

export type TransformResult = {

  success: boolean;

  outputType: string;

  content?: unknown;

  file?: FileAsset | null;

  error?: string;

  warning?: string;
};


/* ============================================================
   BACKEND TEST
   ============================================================ */

export async function testBackend() {

  const response = await fetch(
    `${API_BASE_URL}/api/confirm`
  );


  if (!response.ok) {

    throw new Error(
      `Backend error: ${response.status}`
    );
  }


  return response.json();
}


/* ============================================================
   TRANSFORM CONTENT
   ============================================================ */

export async function transformContent(
  data: {

    sourceText: string;

    outputType: string;

    tone: string;

    audience: string;

    duration?: number;
  }
) {

  const response = await fetch(
    `${API_BASE_URL}/api/transform`,
    {

      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify(data),
    }
  );


  const result =
    await response.json().catch(
      () => null
    );


  if (!response.ok) {

    throw new Error(

      result?.detail ||

      result?.error ||

      `Backend error: ${response.status}`
    );
  }


  return result as TransformResult;
}