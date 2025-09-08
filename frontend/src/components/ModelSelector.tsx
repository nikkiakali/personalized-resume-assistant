export default function ModelSelector({
  model,
  setModel,
}: {
  model: string;
  setModel: (m: string) => void;
}) {
  return (
    <div className="p-4 border rounded-lg bg-white">
      <label className="block font-medium mb-2">Model</label>
      <select
        value={model}
        onChange={(e) => setModel(e.target.value)}
        className="border p-2 rounded"
      >
        <option value="local-llama">Local LLaMA</option>
        <option value="claude-3">Claude 3</option>
        <option value="grok">Grok</option>
      </select>
    </div>
  );
}