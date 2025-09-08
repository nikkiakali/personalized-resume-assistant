import FileUploader from "./components/FileUploader";
import Chat from "./components/Chat";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-100 font-sans text-gray-800">
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold leading-tight text-gray-900">
            Personalized Resume Assistant
          </h1>
        </div>
      </header>
      <main className="max-w-4xl mx-auto p-4 sm:p-6 space-y-8">
        <FileUploader />
        <Chat />
      </main>
    </div>
  );
}