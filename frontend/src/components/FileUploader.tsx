import { useState } from "react";
import { API_BASE } from "../api";

export default function FileUploader() {
  const [status, setStatus] = useState<string>("");

  async function onChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    const form = new FormData();
    form.append("file", file);
    setStatus("Uploading...");

    try {
      const r = await fetch(`${API_BASE}/ingest`, { method: "POST", body: form });

      if (!r.ok) {
        const text = await r.text();
        throw new Error(`${r.status} ${text}`);
      }
      const j = await r.json();
      setStatus(`Indexed ${j.chunks} chunks from ${j.filename}`);
    } catch (err: any) {
      setStatus(`Upload failed: ${err.message}`);
    }
  }

  return (
    <div className="p-4 border rounded-lg bg-white">
      <label className="block font-medium mb-2">
        Upload resume or job description (PDF/DOCX/TXT)
      </label>
      <input type="file" onChange={onChange} />
      <p className="text-sm text-gray-600 mt-2">{status}</p>
    </div>
  );
}