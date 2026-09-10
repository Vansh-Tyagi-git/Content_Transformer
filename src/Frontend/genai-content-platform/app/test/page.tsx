"use client";

import { useState } from "react";
import { testBackend } from "@/lib/api";

export default function TestPage() {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleTest = async () => {
    setLoading(true);
    setMessage("");
    setError("");

    try {
      const result = await testBackend();

      console.log("FastAPI response:", result);

      if (result.success) {
        setMessage(result.message);
      } else {
        setError("Backend returned failure.");
      }
    } catch (err) {
      console.error("Connection error:", err);
      setError("Could not connect to FastAPI.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-full max-w-md">
        
        <h1 className="text-2xl font-bold text-slate-900">
          FastAPI Connection Test
        </h1>

        <p className="text-sm text-slate-500 mt-2 mb-6">
          Testing connection to FastAPI server
        </p>

        <button
          onClick={handleTest}
          disabled={loading}
          className="w-full bg-sky-600 hover:bg-sky-500 text-white py-3 rounded-lg font-semibold disabled:opacity-50"
        >
          {loading ? "Connecting..." : "Test Backend"}
        </button>

        {message && (
          <div className="mt-5 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            ✅ {message}
          </div>
        )}

        {error && (
          <div className="mt-5 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            ❌ {error}
          </div>
        )}
      </div>
    </main>
  );
}