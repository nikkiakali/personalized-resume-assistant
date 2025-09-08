import FileUploader from "./components/FileUploader";
import Chat from "./components/Chat";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        <h1 className="text-2xl font-semibold">Personalized Resume Assistant</h1>
        <FileUploader />
        <Chat />
      </div>
    </div>
  );
}