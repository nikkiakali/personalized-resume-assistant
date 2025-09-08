import { useState } from "react";
import { API_BASE } from "../api";

export default function FileUploader() {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  async function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);

    // Process files sequentially to provide clear feedback
    for (const file of Array.from(files)) {
      const form = new FormData();
      form.append("file", file);

      try {
        const r = await fetch(`${API_BASE}/ingest`, {
          method: "POST",
          body: form,
        });

        if (!r.ok) {
          const text = await r.text();
          throw new Error(`${r.status} ${text}`);
        }
        const j = await r.json();
        const successMessage = `Indexed ${j.chunks} chunks from ${j.filename}`;
        setUploadedFiles((prev) =>
          prev.includes(successMessage) ? prev : [...prev, successMessage]
        );
      } catch (err: any) {
        const errorMessage = `Upload failed for ${file.name}`;
        setUploadedFiles((prev) =>
          prev.includes(errorMessage) ? prev : [...prev, errorMessage]
        );
      }
    }
    setUploading(false);
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm">
      <label
        htmlFor="file-upload"
        className="relative block w-full rounded-lg border-2 border-dashed border-gray-300 p-12 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 cursor-pointer"
      >
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          stroke="currentColor"
          fill="none"
          viewBox="0 0 48 48"
          aria-hidden="true"
        >
          <path
            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <span className="mt-2 block text-sm font-medium text-gray-900">
          {uploading ? "Uploading..." : "Drag & drop files or click to upload"}
        </span>
        <input
          id="file-upload"
          name="file-upload"
          type="file"
          className="sr-only"
          onChange={onFileChange}
          multiple
          disabled={uploading}
        />
      </label>
      {uploadedFiles.length > 0 && (
        <div className="mt-4">
          <h3 className="text-lg font-medium text-gray-900">Active Documents</h3>
          <ul className="mt-2 divide-y divide-gray-200 rounded-md border border-gray-200">
            {uploadedFiles.map((file, i) => (
              <li key={i} className="flex items-center justify-between py-3 pl-4 pr-5 text-sm">
                <div className="flex w-0 flex-1 items-center">
                  <span className="ml-2 w-0 flex-1 truncate">{file}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}