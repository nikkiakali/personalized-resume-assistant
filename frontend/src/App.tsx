import { useState } from "react";
import FileUploader from "./components/FileUploader";
import ModelSelector from "./components/ModelSelector";
import Chat from "./components/Chat";

export default function App() {
  const [model, setModel] = useState("local-llama");
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <h1 className="text-2xl font-semibold">Personalized Resume Assistant</h1>
        <FileUploader />
        <ModelSelector model={model} setModel={setModel} />
        <Chat model={model} />
      </div>
    </div>
  );
}