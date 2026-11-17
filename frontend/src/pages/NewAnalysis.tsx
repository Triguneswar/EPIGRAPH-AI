import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadCloud, X } from "lucide-react";
import { uploadAnalysis } from "../services/api";

const ACCEPTED = ["image/jpeg", "image/png", "image/webp"];
const MAX_MB = 15;

export default function NewAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  function validateAndSet(f: File) {
    if (!ACCEPTED.includes(f.type)) {
      setError("Unsupported format. Please upload JPG, PNG, or WEBP.");
      return;
    }
    if (f.size / (1024 * 1024) > MAX_MB) {
      setError(`File exceeds ${MAX_MB}MB limit.`);
      return;
    }
    setError(null);
    setFile(f);
    setPreview(URL.createObjectURL(f));
  }

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) validateAndSet(f);
  }, []);

  function removeFile() {
    setFile(null);
    setPreview(null);
  }

  async function handleUpload() {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      const analysis = await uploadAnalysis(file);
      navigate(`/analysis/${analysis.id}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-serif font-semibold mb-6">EPIGRAPH-AI Inscription Analysis</h1>

      {!file ? (
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={onDrop}
          className="border-2 border-dashed border-ink/20 rounded-xl p-12 text-center bg-white/40"
        >
          <UploadCloud className="mx-auto mb-3 text-clay" size={32} />
          <p className="text-sm text-ink/70 mb-3">
            Drag and drop an inscription image, or browse your files
          </p>
          <label className="inline-block bg-clay text-parchment px-4 py-2 rounded-md text-sm cursor-pointer hover:bg-bronze transition">
            Browse Files
            <input
              type="file"
              accept={ACCEPTED.join(",")}
              className="hidden"
              onChange={(e) => e.target.files?.[0] && validateAndSet(e.target.files[0])}
            />
          </label>
          <p className="text-xs text-ink/50 mt-3">JPG, PNG, WEBP — up to {MAX_MB}MB</p>
        </div>
      ) : (
        <div className="border border-ink/10 rounded-xl p-4 bg-white/40">
          <div className="flex justify-between items-start mb-3">
            <div>
              <p className="text-sm font-medium">{file.name}</p>
              <p className="text-xs text-ink/60">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button onClick={removeFile} className="text-ink/50 hover:text-red-600">
              <X size={18} />
            </button>
          </div>
          {preview && (
            <img src={preview} alt="preview" className="rounded-lg max-h-72 w-full object-contain bg-ink/5" />
          )}
        </div>
      )}

      {error && <p className="text-sm text-red-600 mt-3">{error}</p>}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="mt-6 bg-clay text-parchment px-6 py-3 rounded-md font-medium hover:bg-bronze transition disabled:opacity-40 flex items-center space-x-2"
      >
        <span>{uploading ? "Analyzing Inscription (Running Full Pipeline)..." : "Analyze Inscription (Run All Steps)"}</span>
      </button>
      {uploading && (
        <p className="text-xs text-ink/60 mt-2 italic animate-pulse">
          Applying vision filters, identifying script, running OCR, reconstructing, and translating to English...
        </p>
      )}
    </div>
  );
}
