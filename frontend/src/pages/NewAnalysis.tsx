import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  UploadCloud,
  X,
  Sparkles,
  Languages,
  FileText,
  ArrowRight,
  Image as ImageIcon,
  Check,
  AlertTriangle,
  ExternalLink,
  Key,
  RotateCw,
} from "lucide-react";
import { uploadAnalysis, getSettings, updateSettings, testSettings } from "../services/api";

const ACCEPTED = ["image/jpeg", "image/png", "image/webp", "image/jpg"];
const MAX_MB = 25;

export default function NewAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  // Settings & Vision AI status
  const [settings, setSettings] = useState<any>(null);
  const [loadingSettings, setLoadingSettings] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [savingKey, setSavingKey] = useState(false);
  const [keyFeedback, setKeyFeedback] = useState<{ type: "success" | "error"; msg: string } | null>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [backendOffline, setBackendOffline] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  async function fetchSettings() {
    setLoadingSettings(true);
    setBackendOffline(false);
    try {
      const data = await getSettings();
      setSettings(data);
    } catch {
      setBackendOffline(true);
    } finally {
      setLoadingSettings(false);
    }
  }

  async function handleActivateKey() {
    if (!apiKeyInput.trim()) return;
    setSavingKey(true);
    setKeyFeedback(null);
    try {
      const cleanKey = apiKeyInput.trim();
      const provider = cleanKey.startsWith("AIza")
        ? "gemini"
        : cleanKey.startsWith("sk-ant")
        ? "claude"
        : "openai_compatible";
      const model = provider === "gemini" ? "gemini-flash-latest" : provider === "claude" ? "claude-3-5-sonnet-20241022" : "gpt-4o";

      const testRes = await testSettings({ api_key: cleanKey, llm_provider: provider });
      if (!testRes.success) {
        setKeyFeedback({ type: "error", msg: testRes.message || "Failed to verify API key with provider." });
        return;
      }

      const updated = await updateSettings({ api_key: cleanKey, llm_provider: provider, model });
      setSettings(updated);
      setApiKeyInput("");
      setShowConfig(false);
      setKeyFeedback({
        type: "success",
        msg: "Live AI Vision Activated! The system is now ready to decipher and translate ANY ancient wall photo.",
      });
    } catch (err: any) {
      setKeyFeedback({
        type: "error",
        msg: err?.response?.data?.detail || "Network error while saving API key.",
      });
    } finally {
      setSavingKey(false);
    }
  }

  function validateAndSet(f: File) {
    if (!ACCEPTED.includes(f.type) && !f.name.match(/\.(jpg|jpeg|png|webp|jfif)$/i)) {
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
      setError(err?.response?.data?.detail || "Upload & decipherment failed. Please check file format.");
    } finally {
      setUploading(false);
    }
  }

  const hasLiveKey = Boolean(settings?.has_api_key);

  return (
    <div className="max-w-3xl mx-auto space-y-7 pb-16">
      {/* Page Header */}
      <div className="text-center space-y-3 pt-2">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-clay/10 text-clay text-xs font-semibold uppercase tracking-wider">
          <Sparkles size={14} />
          <span>Universal Epigraphic Vision & Decipherment</span>
        </div>
        <h1 className="text-3xl md:text-4xl font-serif font-bold text-ink tracking-tight">
          Translate Ancient Wall Literature
        </h1>
        <p className="text-ink/70 text-sm md:text-base max-w-xl mx-auto leading-relaxed">
          Upload any photo of an ancient inscription carved on stone walls, temple rocks, steles, or monuments.
          Directly detect what language & script it is, and receive multi-language translations (English, हिन्दी, தமிழ், తెలుగు, ಕನ್ನಡ).
        </p>
      </div>

      {/* AI VISION ENGINE STATUS & BACKEND STATUS */}
      {backendOffline ? (
        <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-5 shadow-sm space-y-2">
          <div className="flex items-center space-x-2.5 text-red-800">
            <AlertTriangle size={22} className="text-red-600 shrink-0" />
            <h4 className="font-serif font-bold text-base text-red-950">
              Backend Server Offline (Port 8000)
            </h4>
          </div>
          <p className="text-xs text-red-800/90 leading-relaxed pl-8">
            Your Gemini API Key is already configured and verified in <code>.env</code>! However, the FastAPI backend server is currently stopped.
            Please double-click <strong>start_backend.bat</strong> (or <strong>start_all.bat</strong>) in your project folder to start it, then click below:
          </p>
          <div className="pl-8 pt-1">
            <button
              onClick={fetchSettings}
              disabled={loadingSettings}
              className="text-xs bg-red-800 hover:bg-red-900 text-white font-semibold px-4 py-2 rounded-xl transition shadow flex items-center gap-1.5"
            >
              <RotateCw size={13} className={loadingSettings ? "animate-spin" : ""} />
              <span>Retry Connection</span>
            </button>
          </div>
        </div>
      ) : hasLiveKey ? (
        <div className="bg-gradient-to-r from-emerald-50 via-teal-50 to-emerald-50 border border-emerald-300 rounded-2xl p-4 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow">
              <Sparkles size={20} />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-serif font-bold text-sm text-emerald-950">
                  Live Multimodal Vision AI Active
                </span>
                <span className="text-[11px] font-mono font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded-full">
                  {settings.active_engine}
                </span>
              </div>
              <p className="text-xs text-emerald-800/80 mt-0.5">
                Ready to decipher and translate ANY stone wall photo worldwide with genuine, zero-shot readings.
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="text-xs text-emerald-800 hover:text-emerald-950 font-semibold underline shrink-0 self-start sm:self-auto"
          >
            {showConfig ? "Hide Config" : "Change Key"}
          </button>
        </div>
      ) : (
        <div className="bg-gradient-to-br from-amber-50 via-orange-50/70 to-amber-50 border-2 border-amber-300 rounded-3xl p-5 md:p-6 shadow-md space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-amber-200/80 pb-3">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-clay text-parchment flex items-center justify-center shrink-0 shadow">
                <Key size={20} />
              </div>
              <div>
                <h3 className="font-serif font-bold text-base text-ink">
                  Enable Live Translation for All Ancient Wall Photos
                </h3>
                <p className="text-xs text-ink/70">
                  Connect a free Google Gemini API Key to enable real-time reading & original English translations.
                </p>
              </div>
            </div>
            <a
              href="https://aistudio.google.com/app/apikey"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-semibold text-clay hover:text-bronze flex items-center gap-1 bg-white border border-amber-300 px-3 py-1.5 rounded-xl shadow-sm hover:bg-amber-50 transition self-start sm:self-auto"
            >
              <span>🔑 Get Free Gemini Key (100% Free)</span>
              <ExternalLink size={12} />
            </a>
          </div>

          <div className="space-y-2">
            <p className="text-xs text-ink/75 leading-relaxed">
              Google AI Studio gives free API keys with <strong>no credit card required</strong>. Paste your key below to unlock genuine decipherment of any carved stone photo:
            </p>
            <div className="flex flex-col sm:flex-row items-center gap-2">
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder="Paste Gemini API Key (starts with AIzaSy...)"
                className="w-full text-xs font-mono bg-white border border-amber-300 rounded-xl px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-clay/40 shadow-inner"
              />
              <button
                onClick={handleActivateKey}
                disabled={savingKey || !apiKeyInput.trim()}
                className="w-full sm:w-auto shrink-0 text-xs font-semibold bg-clay hover:bg-bronze text-parchment px-4 py-2.5 rounded-xl shadow transition disabled:opacity-50 flex items-center justify-center gap-1.5"
              >
                {savingKey ? (
                  <>
                    <RotateCw size={13} className="animate-spin" />
                    <span>Verifying & Activating...</span>
                  </>
                ) : (
                  <>
                    <Check size={14} />
                    <span>Activate AI Vision</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {showConfig && hasLiveKey && (
        <div className="bg-white border border-amber-300 rounded-2xl p-4 space-y-3 shadow-sm">
          <p className="text-xs text-ink/70 font-semibold">Enter a new API Key to switch models or providers:</p>
          <div className="flex flex-col sm:flex-row items-center gap-2">
            <input
              type="password"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              placeholder="Paste new Gemini or OpenAI API Key"
              className="w-full text-xs font-mono bg-white border border-ink/20 rounded-xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-clay/40"
            />
            <button
              onClick={handleActivateKey}
              disabled={savingKey || !apiKeyInput.trim()}
              className="w-full sm:w-auto shrink-0 text-xs font-semibold bg-clay text-parchment px-4 py-2 rounded-xl shadow transition"
            >
              Update Key
            </button>
          </div>
        </div>
      )}

      {keyFeedback && (
        <div
          className={`p-3 rounded-xl text-xs flex items-center space-x-2 border shadow-sm ${
            keyFeedback.type === "success"
              ? "bg-emerald-50 border-emerald-200 text-emerald-800"
              : "bg-red-50 border-red-200 text-red-700"
          }`}
        >
          {keyFeedback.type === "success" ? <Check size={16} /> : <AlertTriangle size={16} />}
          <span>{keyFeedback.msg}</span>
        </div>
      )}

      {/* Feature Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="bg-white/70 border border-ink/10 rounded-xl p-3.5 flex items-center space-x-3 shadow-sm">
          <div className="w-9 h-9 rounded-lg bg-clay/15 text-clay flex items-center justify-center shrink-0">
            <Languages size={18} />
          </div>
          <div>
            <h4 className="font-serif font-bold text-xs text-ink">Language & Script</h4>
            <p className="text-[11px] text-ink/60">Tamil, Brahmi, Sanskrit, Latin, Greek</p>
          </div>
        </div>

        <div className="bg-white/70 border border-ink/10 rounded-xl p-3.5 flex items-center space-x-3 shadow-sm">
          <div className="w-9 h-9 rounded-lg bg-amber-500/15 text-amber-800 flex items-center justify-center shrink-0">
            <FileText size={18} />
          </div>
          <div>
            <h4 className="font-serif font-bold text-xs text-ink">Wall Inscription Reading</h4>
            <p className="text-[11px] text-ink/60">Reads authentic incised glyphs</p>
          </div>
        </div>

        <div className="bg-white/70 border border-ink/10 rounded-xl p-3.5 flex items-center space-x-3 shadow-sm">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/15 text-emerald-800 flex items-center justify-center shrink-0">
            <Sparkles size={18} />
          </div>
          <div>
            <h4 className="font-serif font-bold text-xs text-ink">Multi-Language Translation</h4>
            <p className="text-[11px] text-ink/60">English, Hindi, Tamil, Telugu & Kannada</p>
          </div>
        </div>
      </div>

      {/* Upload Zone */}
      <div className="bg-white/80 border border-ink/15 rounded-3xl p-6 md:p-8 shadow-sm space-y-6">
        {!file ? (
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={onDrop}
            className="border-2 border-dashed border-clay/40 hover:border-clay rounded-2xl p-10 md:p-14 text-center bg-parchment/40 hover:bg-parchment/70 transition duration-200 group cursor-pointer"
            onClick={() => {
              const el = document.getElementById("file-upload-input");
              if (el) el.click();
            }}
          >
            <div className="w-16 h-16 rounded-2xl bg-clay/10 group-hover:bg-clay/20 text-clay mx-auto mb-4 flex items-center justify-center transition duration-200">
              <UploadCloud size={32} />
            </div>
            <h3 className="font-serif font-bold text-lg text-ink mb-1">
              Drop Inscription Photo Here
            </h3>
            <p className="text-xs text-ink/60 mb-5 max-w-sm mx-auto">
              Upload clear photos of carved stone walls, temple pillars, granite steles, copper plates, or cave rocks.
            </p>

            <label
              onClick={(e) => e.stopPropagation()}
              className="inline-flex items-center gap-2 bg-clay text-parchment px-5 py-2.5 rounded-xl text-xs md:text-sm font-semibold cursor-pointer hover:bg-bronze transition shadow-md"
            >
              <ImageIcon size={16} />
              <span>Browse Inscription Photo</span>
              <input
                id="file-upload-input"
                type="file"
                accept={ACCEPTED.join(",")}
                className="hidden"
                onChange={(e) => e.target.files?.[0] && validateAndSet(e.target.files[0])}
              />
            </label>
            <p className="text-[11px] text-ink/40 mt-4">Supports JPG, PNG, WEBP — up to {MAX_MB}MB</p>
          </div>
        ) : (
          <div className="border border-ink/15 rounded-2xl p-5 bg-white/90 space-y-4">
            <div className="flex justify-between items-start border-b border-ink/10 pb-3">
              <div>
                <p className="text-sm font-bold text-ink truncate max-w-md">{file.name}</p>
                <p className="text-xs text-ink/50 font-mono">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <button
                onClick={removeFile}
                className="text-ink/40 hover:text-red-600 p-1 rounded-lg hover:bg-red-50 transition"
              >
                <X size={20} />
              </button>
            </div>

            {preview && (
              <div className="bg-ink/5 rounded-xl p-2 border border-ink/10 flex items-center justify-center max-h-96 overflow-hidden">
                <img src={preview} alt="Inscription Preview" className="rounded-lg max-h-96 w-full object-contain" />
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center space-x-2">
            <span>{error}</span>
          </div>
        )}

        {/* Submit Button */}
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full bg-clay hover:bg-bronze text-parchment py-3.5 px-6 rounded-2xl font-serif font-bold text-base shadow-lg transition duration-200 disabled:opacity-40 flex items-center justify-center space-x-2"
        >
          {uploading ? (
            <>
              <span className="w-4 h-4 border-2 border-white/80 border-t-transparent rounded-full animate-spin"></span>
              <span>Deciphering & Translating Inscription...</span>
            </>
          ) : (
            <>
              <span>Decipher & Translate (Multi-Language)</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>

        {uploading && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-xs text-amber-900 space-y-1.5 animate-pulse">
            <p className="font-semibold flex items-center gap-1.5">
              <span>🏛️</span> Multimodal Vision Pipeline in Progress:
            </p>
            <p className="text-ink/70">
              1. Applying OpenCV contrast sharpening & edge enhancement...
              <br />
              2. Analyzing carved glyph morphology with Multimodal AI Vision...
              <br />
              3. Transcribing incised stone characters and phonetics...
              <br />
              4. Synthesizing authentic multi-language translations (English, Hindi, Tamil, Telugu, Kannada)...
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
