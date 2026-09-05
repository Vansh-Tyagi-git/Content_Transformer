const API_BASE_URL = "http://127.0.0.1:8000";

export async function testBackend() {
  const response = await fetch(`${API_BASE_URL}/api/confirm`);

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status}`);
  }

  return response.json();
}

export async function transformContent(data: {
  sourceText: string;
  outputType: string;
  tone: string;
  audience: string;
}) {
  const response = await fetch(`${API_BASE_URL}/api/transform`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status}`);
  }

  return response.json();
}