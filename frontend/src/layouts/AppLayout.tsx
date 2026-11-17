import { useState, useEffect } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, ScanSearch, History, Scroll, Sparkles, Settings as SettingsIcon, Check, Key, ExternalLink, X, AlertCircle } from "lucide-react";
import { getSettings, updateSettings, testSettings } from "../services/api";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/analysis/new", label: "New Inscription", icon: ScanSearch },
  { to: "/history", label: "History", icon: History },
];

export default function AppLayout() {
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [settings, setSettings] = useState<any>(null);
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [provider, setProvider] = useState("gemini");
  const [model, setModel] = useState("gemini-2.0-flash");
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  async function loadSettings() {
    try {
      const data = await getSettings();
      setSettings(data);
      if (data.llm_provider) setProvider(data.llm_provider);
      if (data.model) setModel(data.model);
    } catch (err) {
      console.error("Failed to load settings", err);
    }
  }

  useEffect(() => {
    loadSettings();
  }, []);

  async function handleSave() {
    setSaving(true);
    setTestResult(null);
    try {
      const updated = await updateSettings({
        api_key: apiKeyInput.trim() ? apiKeyInput.trim() : undefined,
        llm_provider: provider,
        model: model,
      });
      setSettings(updated);
      setApiKeyInput("");
      setTestResult({ success: true, message: "Settings saved successfully! Vision engine updated." });
      setTimeout(() => {
        setSettingsModalOpen(false);
        setTestResult(null);
      }, 1500);
    } catch (err: any) {
      setTestResult({ success: false, message: err?.response?.data?.detail || "Failed to save settings." });
    } finally {
      setSaving(false);
    }
  }

  async function handleTest() {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await testSettings({
        api_key: apiKeyInput.trim() || undefined,
        llm_provider: provider,
      });
      setTestResult(res);
    } catch (err: any) {
      setTestResult({ success: false, message: err?.response?.data?.detail || "Connection test failed." });
    } finally {
      setTesting(false);
    }
  }

  return (
    <div className="min-h-screen flex bg-parchment">
      {/* Sidebar */}
      <aside className="w-64 bg-ink text-parchment flex flex-col p-4 shadow-xl z-20">
        <div className="flex items-center gap-2.5 mb-8 px-2 pt-2">
          <div className="w-9 h-9 rounded-xl bg-clay/20 flex items-center justify-center text-bronze shadow-inner">
            <Scroll size={22} />
          </div>
          <div>
            <span className="font-bold tracking-wide text-base block font-serif">EPIGRAPH-AI</span>
            <span className="text-[10px] text-parchment/60 tracking-wider uppercase block">Wall Literature Decipherer</span>
          </div>
        </div>

        <nav className="flex-1 space-y-2">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm transition font-medium ${
                  isActive ? "bg-clay text-parchment shadow-md" : "hover:bg-white/10 text-parchment/80"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* AI Engine Status Card */}
        <div className="mt-auto pt-4 border-t border-white/10 space-y-3">
          <div className="bg-white/5 border border-white/10 rounded-xl p-3">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-parchment/60 flex items-center gap-1.5">
                <Sparkles size={13} className={settings?.is_multimodal_live ? "text-amber-400" : "text-clay"} />
                AI Decipherer
              </span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                settings?.is_multimodal_live ? "bg-emerald-900/60 text-emerald-300 border border-emerald-500/30" : "bg-amber-900/60 text-amber-300 border border-amber-500/30"
              }`}>
                {settings?.is_multimodal_live ? "Live Vision" : "Local Engine"}
              </span>
            </div>
            <p className="text-xs text-parchment/90 font-mono truncate">
              {settings?.active_engine || "Initializing..."}
            </p>
            <button
              onClick={() => setSettingsModalOpen(true)}
              className="mt-2.5 w-full flex items-center justify-center gap-1.5 text-xs bg-white/10 hover:bg-white/20 text-parchment py-1.5 px-2.5 rounded-lg transition"
            >
              <SettingsIcon size={13} />
              <span>Configure AI Key</span>
            </button>
          </div>

          <div className="text-[11px] text-parchment/40 px-1 text-center">
            Ancient Inscriptions · Digital Archaeology
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto max-h-screen">
        <Outlet />
      </main>

      {/* AI Settings Modal */}
      {settingsModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-ink/10 w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Header */}
            <div className="bg-gradient-to-r from-ink to-ink/90 text-parchment p-5 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-clay/30 flex items-center justify-center text-amber-300">
                  <Sparkles size={18} />
                </div>
                <div>
                  <h3 className="font-serif font-bold text-lg leading-tight">AI Vision & Decipherment Settings</h3>
                  <p className="text-xs text-parchment/70">Enable deep multimodal vision to read eroded stone carvings</p>
                </div>
              </div>
              <button
                onClick={() => setSettingsModalOpen(false)}
                className="text-parchment/60 hover:text-white p-1 rounded-lg hover:bg-white/10 transition"
              >
                <X size={20} />
              </button>
            </div>

            {/* Form */}
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-ink/70 uppercase tracking-wider mb-1.5">
                  Vision Provider
                </label>
                <select
                  value={provider}
                  onChange={(e) => {
                    const p = e.target.value;
                    setProvider(p);
                    if (p === "gemini") setModel("gemini-2.0-flash");
                    else if (p === "openai_compatible") setModel("gpt-4o");
                    else if (p === "claude") setModel("claude-3-5-sonnet-20241022");
                  }}
                  className="w-full text-sm border border-ink/20 rounded-xl p-2.5 bg-ink/5 focus:outline-none focus:ring-2 focus:ring-clay font-medium"
                >
                  <option value="gemini">Google Gemini 2.0 / 1.5 (Recommended - Free & Best for Epigraphy)</option>
                  <option value="openai_compatible">OpenAI GPT-4o / Compatible</option>
                  <option value="claude">Anthropic Claude 3.5 Sonnet</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-ink/70 uppercase tracking-wider mb-1.5">
                  Vision Model
                </label>
                <input
                  type="text"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  placeholder="e.g. gemini-flash-latest or gpt-4o"
                  className="w-full text-sm border border-ink/20 rounded-xl p-2.5 bg-ink/5 focus:outline-none focus:ring-2 focus:ring-clay font-mono"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-semibold text-ink/70 uppercase tracking-wider">
                    API Key
                  </label>
                  {settings?.has_api_key && (
                    <span className="text-xs text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-mono">
                      Current: {settings.masked_key}
                    </span>
                  )}
                </div>
                <div className="relative">
                  <input
                    type="password"
                    value={apiKeyInput}
                    onChange={(e) => setApiKeyInput(e.target.value)}
                    placeholder={settings?.has_api_key ? "Leave blank to keep existing key, or paste new key" : "Paste your API key here..."}
                    className="w-full text-sm border border-ink/20 rounded-xl p-2.5 pl-9 bg-ink/5 focus:outline-none focus:ring-2 focus:ring-clay font-mono"
                  />
                  <Key size={16} className="absolute left-3 top-3 text-ink/40" />
                </div>
              </div>

              {/* Free Key Helper */}
              {provider === "gemini" && (
                <div className="bg-amber-50 border border-amber-200/80 rounded-xl p-3 text-xs text-amber-900 space-y-1">
                  <p className="font-semibold flex items-center gap-1.5">
                    <span>💡</span> Get a Free Gemini API Key in 10 seconds:
                  </p>
                  <p className="text-ink/80">
                    Google AI Studio provides free, fast API keys with generous limits.
                  </p>
                  <a
                    href="https://aistudio.google.com/app/apikey"
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-clay font-semibold hover:underline pt-0.5"
                  >
                    <span>Create Free Key at aistudio.google.com</span>
                    <ExternalLink size={12} />
                  </a>
                </div>
              )}

              {/* Test feedback */}
              {testResult && (
                <div className={`p-3 rounded-xl text-xs flex items-start gap-2 border ${
                  testResult.success ? "bg-emerald-50 border-emerald-200 text-emerald-800" : "bg-red-50 border-red-200 text-red-800"
                }`}>
                  {testResult.success ? <Check size={16} className="shrink-0 mt-0.5 text-emerald-600" /> : <AlertCircle size={16} className="shrink-0 mt-0.5 text-red-600" />}
                  <span>{testResult.message}</span>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-3 pt-2 border-t border-ink/10">
                <button
                  type="button"
                  onClick={handleTest}
                  disabled={testing || saving}
                  className="px-4 py-2 text-xs font-semibold text-ink/80 hover:bg-ink/5 border border-ink/15 rounded-xl transition disabled:opacity-50"
                >
                  {testing ? "Testing..." : "Test Connection"}
                </button>
                <button
                  type="button"
                  onClick={handleSave}
                  disabled={saving || testing}
                  className="px-5 py-2 text-xs font-semibold bg-clay hover:bg-bronze text-parchment rounded-xl shadow transition disabled:opacity-50 flex items-center gap-1.5"
                >
                  <Check size={14} />
                  <span>{saving ? "Saving..." : "Save & Activate"}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
