import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getAnalysis, runPipeline, runStep, updateSettings, testSettings } from "../services/api";
import {
  RotateCw,
  CheckCircle2,
  AlertTriangle,
  Languages,
  FileText,
  Image as ImageIcon,
  Sparkles,
  Copy,
  Check,
  Calendar,
  Compass,
  ArrowRight,
  ShieldCheck,
  BookOpen,
  Key,
  ExternalLink,
} from "lucide-react";

export default function AnalysisResult() {
  const { id } = useParams<{ id: string }>();
  const [analysis, setAnalysis] = useState<any>(null);
  const [running, setRunning] = useState<boolean>(false);
  const [runningStep, setRunningStep] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [selectedLang, setSelectedLang] = useState<string>("en");
  const [copiedLang, setCopiedLang] = useState<string | null>(null);
  const [activeImageTab, setActiveImageTab] = useState<"original" | "processed">("original");

  // Inline AI Vision Activation for Offline Runs
  const [inlineKey, setInlineKey] = useState("");
  const [activatingKey, setActivatingKey] = useState(false);
  const [inlineError, setInlineError] = useState<string | null>(null);

  async function handleActivateAndRerun() {
    if (!inlineKey.trim() || !id) return;
    setActivatingKey(true);
    setInlineError(null);
    try {
      const cleanKey = inlineKey.trim();
      const provider = cleanKey.startsWith("AIza")
        ? "gemini"
        : cleanKey.startsWith("sk-ant")
        ? "claude"
        : "openai_compatible";
      const model = provider === "gemini" ? "gemini-flash-latest" : provider === "claude" ? "claude-3-5-sonnet-20241022" : "gpt-4o";

      const testRes = await testSettings({ api_key: cleanKey, llm_provider: provider });
      if (!testRes.success) {
        setInlineError(testRes.message || "Failed to verify API key with provider.");
        return;
      }

      await updateSettings({ api_key: cleanKey, llm_provider: provider, model });
      const updated = await runPipeline(id);
      setAnalysis(updated);
      setInlineKey("");
    } catch (err: any) {
      setInlineError(err?.response?.data?.detail || "Failed to activate key and re-run decipherment.");
    } finally {
      setActivatingKey(false);
    }
  }

  async function loadData() {
    if (!id) return;
    try {
      const data = await getAnalysis(id);
      setAnalysis(data);
      // Auto-run if only uploaded and not analyzed yet
      if (data.status === "UPLOADED" && !data.translation && !data.ocr_result) {
        handleRunAll();
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to load analysis");
    }
  }

  useEffect(() => {
    loadData();
  }, [id]);

  async function handleRunAll() {
    if (!id) return;
    setRunning(true);
    setError(null);
    try {
      const updated = await runPipeline(id);
      setAnalysis(updated);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to complete full pipeline analysis");
    } finally {
      setRunning(false);
    }
  }

  async function handleRunStep(stepKey: string) {
    if (!id) return;
    setRunningStep(stepKey);
    setError(null);
    try {
      await runStep(id, stepKey);
      const updated = await getAnalysis(id);
      setAnalysis(updated);
    } catch (err: any) {
      setError(err?.response?.data?.detail || `Failed to run ${stepKey}`);
    } finally {
      setRunningStep(null);
    }
  }

  function handleCopyTranslation() {
    if (!analysis?.translation?.english) return;
    navigator.clipboard.writeText(analysis.translation.english);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (!analysis) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4 text-ink/70">
        <RotateCw className="animate-spin text-clay" size={32} />
        <span className="font-serif text-lg">Deciphering ancient inscription...</span>
        <p className="text-xs text-ink/50">Analyzing paleographic glyph structures and historical language</p>
      </div>
    );
  }

  const translation = analysis.translation;
  const script = analysis.script_prediction;
  const ocr = analysis.ocr_result;
  const reconstruction = analysis.reconstruction;
  const preprocess = analysis.preprocessing;
  const isComplete = Boolean(translation && ocr);
  const isOffline =
    !translation?.provider ||
    translation.provider.includes("Offline Mode") ||
    translation.provider.includes("Key Required") ||
    translation.provider.includes("Adaptive Paleographic");

  // Extract detected language, era, and transliteration
  const metaSpan = translation?.uncertain_spans?.[0] || {};
  const multilingual = (translation as any)?.multilingual || metaSpan?.multilingual || {};
  const firstAlt = script?.alternatives?.[0] || {};
  const detectedLanguage = metaSpan.language || firstAlt.language || "Ancient Inscription Language";
  const detectedEra = metaSpan.era || firstAlt.period || "Historical Epigraphic Era";
  const transliteration = metaSpan.transliteration || "";

  // Clean translation text to remove redundant header if embedded
  let cleanEnglish = translation?.english || "";
  if (cleanEnglish.startsWith("[")) {
    const endBracket = cleanEnglish.indexOf("]\n\n");
    if (endBracket !== -1) {
      cleanEnglish = cleanEnglish.substring(endBracket + 3).trim();
    }
  }

  const hindiTranslation = metaSpan?.hindi || multilingual?.hi || multilingual?.hindi || "";
  const tamilTranslation = translation?.modern_tamil || metaSpan?.tamil || multilingual?.ta || multilingual?.tamil || "";
  const teluguTranslation = metaSpan?.telugu || multilingual?.te || multilingual?.telugu || "";
  const kannadaTranslation = metaSpan?.kannada || multilingual?.kn || multilingual?.kannada || "";
  const vernacularTranslation = metaSpan?.vernacular || multilingual?.vernacular || "";

  const languageTabs = [
    {
      id: "en",
      name: "English",
      nativeName: "English",
      flag: "🇬🇧",
      text: cleanEnglish,
      title: "English Translation of Wall Literature",
      subtitle: "Direct contextual translation of the literature incised on the stone wall",
      badge: "Primary",
      fontClass: "font-serif italic",
    },
    {
      id: "hi",
      name: "Hindi",
      nativeName: "हिन्दी",
      flag: "🇮🇳",
      text: hindiTranslation,
      title: "सम्पूर्ण हिन्दी अनुवाद (Hindi Translation)",
      subtitle: "शिलालेख पर उत्कीर्ण मूल साहित्य का प्रामाणिक हिन्दी अनुवाद",
      badge: "National",
      fontClass: "font-sans",
    },
    {
      id: "ta",
      name: "Tamil",
      nativeName: "தமிழ்",
      flag: "🏛️",
      text: tamilTranslation,
      title: "முழுமையான தமிழ் உரை விளக்கம் (Tamil Translation)",
      subtitle: "கற்பலகையில் பொறிக்கப்பட்ட வரலாற்றுச் சாசனத்தின் நேரடி உரை விளக்கம்",
      badge: "Classical",
      fontClass: "font-tamil",
    },
    {
      id: "te",
      name: "Telugu",
      nativeName: "తెలుగు",
      flag: "🇮🇳",
      text: teluguTranslation,
      title: "పూర్తి తెలుగు అనువాదం (Telugu Translation)",
      subtitle: "శిలాశాసనంపై చెక్కబడిన ప్రాచీన రచన యొక్క ప్రామాణిక తెలుగు అనువాదం",
      badge: "Classical",
      fontClass: "font-sans",
    },
    {
      id: "kn",
      name: "Kannada",
      nativeName: "ಕನ್ನಡ",
      flag: "🇮🇳",
      text: kannadaTranslation,
      title: "ಸಂಪೂರ್ಣ ಕನ್ನಡ ಅನುವಾದ (Kannada Translation)",
      subtitle: "ಶಿಲಾಶಾಸನದಲ್ಲಿ ಕೆತ್ತಲಾದ ಸಾಹಿತ್ಯದ ನೇರ ಕನ್ನಡ ವಿವರಣೆ",
      badge: "Classical",
      fontClass: "font-sans",
    },
    {
      id: "vernacular",
      name: "Vernacular",
      nativeName: "பிராந்திய உரை",
      flag: "🌐",
      text: vernacularTranslation,
      title: "Regional / Vernacular Reading",
      subtitle: "Authentic vernacular interpretation matching the regional culture of the inscription",
      badge: "Regional",
      fontClass: "font-serif",
    },
  ];

  const activeTab = languageTabs.find((t) => t.id === selectedLang) || languageTabs[0];
  const activeText = activeTab.text || cleanEnglish;

  function handleCopyActive() {
    if (!activeText) return;
    navigator.clipboard.writeText(activeText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  function handleCopySpecific(text: string, langId: string) {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedLang(langId);
    setTimeout(() => setCopiedLang(null), 2000);
  }

  return (
    <div className="max-w-5xl mx-auto space-y-7 pb-16">
      {/* Top Bar Navigation & Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-ink/10 pb-5">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-2xl md:text-3xl font-serif font-bold text-ink tracking-tight">
              Epigraphic Decipherment
            </h1>
            <span className="text-xs px-2.5 py-1 rounded-md font-mono font-semibold bg-clay/15 text-clay border border-clay/20">
              #{analysis.id.slice(0, 8)}
            </span>
          </div>
          <div className="flex items-center space-x-3 mt-1.5 text-xs">
            <span className="font-semibold uppercase tracking-wider text-ink/50">Status:</span>
            {isComplete ? (
              <span className="inline-flex items-center font-medium text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                <CheckCircle2 size={13} className="mr-1 text-emerald-600" /> Deciphered & Translated
              </span>
            ) : (
              <span className="font-medium text-amber-800 bg-amber-50 border border-amber-200 px-2.5 py-0.5 rounded-full animate-pulse">
                {analysis.status}...
              </span>
            )}
            <span className="text-ink/40">·</span>
            <span className="text-ink/60 font-mono text-[11px]">
              Engine: {translation?.provider || script?.provider || "EPIGRAPH-AI Vision Engine"}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to="/analysis/new"
            className="text-xs font-semibold text-ink/80 hover:text-ink px-3.5 py-2 rounded-xl border border-ink/20 hover:bg-white/80 transition shadow-sm flex items-center gap-1.5"
          >
            <Compass size={14} />
            <span>Upload Another Photo</span>
          </Link>

          <button
            onClick={handleRunAll}
            disabled={running}
            className="flex items-center space-x-2 text-xs md:text-sm bg-clay hover:bg-bronze text-parchment font-semibold px-4 py-2 rounded-xl shadow-md transition disabled:opacity-50"
          >
            {running ? (
              <>
                <RotateCw size={15} className="animate-spin" />
                <span>Deciphering Inscription...</span>
              </>
            ) : (
              <>
                <Sparkles size={15} />
                <span>Re-run Full Analysis</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-800 text-sm rounded-xl flex items-center space-x-3 shadow-sm">
          <AlertTriangle size={18} className="shrink-0 text-red-600" />
          <span>{error}</span>
        </div>
      )}

      {/* HIGHLIGHT 1: DETECTED LANGUAGE, SCRIPT & HISTORICAL ERA PILLS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {/* Language */}
        <div className="bg-white/90 border border-amber-200/90 rounded-2xl p-4 shadow-sm flex items-start space-x-3">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center text-clay shrink-0">
            <Languages size={20} />
          </div>
          <div className="min-w-0">
            <span className="text-[11px] font-bold text-ink/50 uppercase tracking-wider block">Detected Language</span>
            <p className="font-serif font-bold text-base text-ink truncate mt-0.5" title={detectedLanguage}>
              {detectedLanguage}
            </p>
          </div>
        </div>

        {/* Script */}
        <div className="bg-white/90 border border-amber-200/90 rounded-2xl p-4 shadow-sm flex items-start space-x-3">
          <div className="w-10 h-10 rounded-xl bg-clay/10 flex items-center justify-center text-clay shrink-0">
            <FileText size={20} />
          </div>
          <div className="min-w-0">
            <span className="text-[11px] font-bold text-ink/50 uppercase tracking-wider block">Carved Script</span>
            <p className="font-serif font-bold text-base text-clay truncate mt-0.5" title={script?.script || "Identifying..."}>
              {script?.script || "Analyzing..."}
            </p>
          </div>
        </div>

        {/* Era & Dynasty */}
        <div className="bg-white/90 border border-amber-200/90 rounded-2xl p-4 shadow-sm flex items-start space-x-3">
          <div className="w-10 h-10 rounded-xl bg-orange-500/10 flex items-center justify-center text-orange-700 shrink-0">
            <Calendar size={20} />
          </div>
          <div className="min-w-0">
            <span className="text-[11px] font-bold text-ink/50 uppercase tracking-wider block">Historical Period</span>
            <p className="font-serif font-semibold text-xs text-ink/90 line-clamp-2 mt-0.5" title={detectedEra}>
              {detectedEra}
            </p>
          </div>
        </div>

        {/* Confidence */}
        <div className="bg-white/90 border border-amber-200/90 rounded-2xl p-4 shadow-sm flex items-start space-x-3">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-700 shrink-0">
            <ShieldCheck size={20} />
          </div>
          <div>
            <span className="text-[11px] font-bold text-ink/50 uppercase tracking-wider block">Paleographic Match</span>
            <p className="font-mono font-bold text-lg text-emerald-800 mt-0.5">
              {script ? `${Math.round(script.confidence * 100)}%` : "--%"}
            </p>
          </div>
        </div>
      </div>

      {/* HIGHLIGHT 2: MULTI-LANGUAGE TRANSLATION CARD */}
      <div className="bg-gradient-to-br from-amber-50/90 via-white to-orange-50/70 border-2 border-amber-300 rounded-3xl p-6 md:p-8 shadow-lg space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-amber-200/70 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-11 h-11 rounded-2xl bg-clay text-parchment flex items-center justify-center shadow-md">
              <Languages size={24} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-serif font-bold text-2xl text-ink tracking-tight">
                  {activeTab.title}
                </h2>
                <span className="hidden sm:inline-block px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-200/70 text-ink/80 border border-amber-300">
                  {activeTab.badge}
                </span>
              </div>
              <p className="text-xs text-ink/60 mt-0.5">
                {activeTab.subtitle}
              </p>
            </div>
          </div>

          {translation && (
            <div className="flex items-center gap-2 self-start sm:self-auto">
              <button
                onClick={handleCopyActive}
                className="flex items-center space-x-1.5 text-xs font-semibold px-3.5 py-1.5 rounded-xl border border-amber-300 bg-white hover:bg-amber-50 text-ink/80 transition shadow-sm"
              >
                {copied ? <Check size={14} className="text-emerald-600" /> : <Copy size={14} className="text-clay" />}
                <span>{copied ? "Copied!" : `Copy ${activeTab.name}`}</span>
              </button>
            </div>
          )}
        </div>

        {/* Multi-Language Selector Tabs */}
        <div className="flex flex-wrap items-center gap-2">
          {languageTabs.map((lang) => {
            const isSelected = selectedLang === lang.id;
            const hasText = Boolean(lang.text);
            return (
              <button
                key={lang.id}
                onClick={() => setSelectedLang(lang.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition shadow-sm ${
                  isSelected
                    ? "bg-clay text-parchment shadow-md ring-2 ring-clay/30"
                    : "bg-white/85 text-ink/80 border border-amber-300 hover:bg-amber-100/70"
                }`}
              >
                <span className="text-sm">{lang.flag}</span>
                <span className="font-medium">{lang.name}</span>
                <span className={`text-[11px] ${isSelected ? "text-amber-200" : "text-ink/50"}`}>
                  ({lang.nativeName})
                </span>
                {hasText && (
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      isSelected ? "bg-amber-300" : "bg-emerald-500"
                    }`}
                    title="Translation available"
                  />
                )}
              </button>
            );
          })}
        </div>

        {translation ? (
          <div className="space-y-5">
            {/* Inline AI Vision Key Activation Banner for Offline Runs */}
            {isOffline && (
              <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-300 rounded-2xl p-5 shadow-sm space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-amber-200/60 pb-2">
                  <div className="flex items-center space-x-2">
                    <Key size={18} className="text-clay shrink-0" />
                    <h4 className="font-serif font-bold text-sm text-ink">
                      Decipher This Specific Stone with Live Multimodal AI
                    </h4>
                  </div>
                  <a
                    href="https://aistudio.google.com/app/apikey"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-clay hover:text-bronze font-semibold flex items-center gap-1 self-start sm:self-auto"
                  >
                    <span>Get Free Key (Google AI Studio)</span>
                    <ExternalLink size={12} />
                  </a>
                </div>
                <p className="text-xs text-ink/75 leading-relaxed">
                  This photo was analyzed in offline structural mode. To read the exact carved characters and generate authentic multi-language translations (English, Hindi, Tamil, Telugu, Kannada), enter your free Gemini API key below:
                </p>
                <div className="flex flex-col sm:flex-row items-center gap-2">
                  <input
                    type="password"
                    value={inlineKey}
                    onChange={(e) => setInlineKey(e.target.value)}
                    placeholder="Paste Gemini API Key (starts with AIzaSy...)"
                    className="w-full text-xs font-mono bg-white border border-amber-300 rounded-xl px-3.5 py-2.5 focus:outline-none focus:ring-2 focus:ring-clay/40"
                  />
                  <button
                    onClick={handleActivateAndRerun}
                    disabled={activatingKey || !inlineKey.trim()}
                    className="w-full sm:w-auto shrink-0 text-xs font-semibold bg-clay hover:bg-bronze text-parchment px-4 py-2.5 rounded-xl shadow transition disabled:opacity-50 flex items-center justify-center gap-1.5"
                  >
                    {activatingKey ? (
                      <>
                        <RotateCw size={13} className="animate-spin" />
                        <span>Deciphering with Live AI...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles size={14} />
                        <span>Decipher & Translate Now</span>
                      </>
                    )}
                  </button>
                </div>
                {inlineError && (
                  <p className="text-xs text-red-600 font-medium">{inlineError}</p>
                )}
              </div>
            )}

            {/* Active Language Translation Box */}
            <div className="bg-white/95 border border-amber-200/80 rounded-2xl p-6 shadow-sm relative space-y-3">
              <div className="flex items-center justify-between border-b border-amber-100 pb-2">
                <div className="text-xs font-mono font-bold text-clay uppercase tracking-widest flex items-center gap-1.5">
                  <BookOpen size={14} />
                  <span>
                    {activeTab.name} Literature Reading ({activeTab.nativeName})
                  </span>
                </div>
                <span className="text-[11px] font-mono text-ink/50 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                  {detectedLanguage} · {detectedEra}
                </span>
              </div>

              {activeTab.text ? (
                <p className={`text-lg md:text-xl text-ink leading-relaxed ${activeTab.fontClass} text-ink/90`}>
                  "{activeTab.text}"
                </p>
              ) : (
                <div className="bg-amber-50/60 border border-dashed border-amber-300 rounded-xl p-5 text-center space-y-2">
                  <Languages className="mx-auto text-clay/70" size={24} />
                  <h4 className="font-serif font-bold text-sm text-ink">
                    {activeTab.name} ({activeTab.nativeName}) Translation
                  </h4>
                  <p className="text-xs text-ink/70 max-w-md mx-auto">
                    Multi-language translation for {activeTab.name} will be synthesized by the vision engine. Click "Re-translate Inscription" below to regenerate all 5 languages.
                  </p>
                  <button
                    onClick={() => handleRunStep("translate")}
                    disabled={runningStep === "translate"}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 bg-clay text-parchment rounded-xl shadow hover:bg-bronze transition"
                  >
                    <RotateCw size={12} className={runningStep === "translate" ? "animate-spin" : ""} />
                    <span>Generate Multi-Language Translations</span>
                  </button>
                </div>
              )}
            </div>

            {/* Compare All Languages At a Glance */}
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between">
                <h4 className="font-serif font-bold text-sm text-ink flex items-center gap-2">
                  <span>🌐</span>
                  <span>Comparative Multi-Language Readings:</span>
                </h4>
                <span className="text-[11px] text-ink/50">Click any card to focus</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {languageTabs
                  .filter((lang) => lang.id !== activeTab.id && Boolean(lang.text))
                  .map((lang) => (
                    <div
                      key={lang.id}
                      onClick={() => setSelectedLang(lang.id)}
                      className="bg-amber-50/70 hover:bg-amber-100/80 border border-amber-200 rounded-2xl p-4 shadow-sm cursor-pointer transition space-y-2 group"
                    >
                      <div className="flex items-center justify-between border-b border-amber-200/60 pb-1.5">
                        <span className="text-xs font-bold text-clay uppercase tracking-wider flex items-center gap-1.5">
                          <span>{lang.flag}</span>
                          <span>{lang.name} ({lang.nativeName})</span>
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCopySpecific(lang.text, lang.id);
                          }}
                          className="text-[11px] text-clay hover:text-bronze flex items-center gap-1 font-semibold opacity-80 group-hover:opacity-100"
                        >
                          {copiedLang === lang.id ? (
                            <>
                              <Check size={11} className="text-emerald-600" />
                              <span className="text-emerald-600">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy size={11} />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                      <p className={`text-sm text-ink/80 line-clamp-3 leading-relaxed ${lang.fontClass}`}>
                        {lang.text}
                      </p>
                    </div>
                  ))}
              </div>
            </div>

            {/* Inscription Meta Footer */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs text-ink/50 pt-2 gap-2 border-t border-amber-200/60">
              <span className="flex items-center gap-2">
                <span>Decipherment Model:</span>
                <span className="font-mono text-clay font-medium">{translation.provider}</span>
                <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                  Multi-Language Enabled
                </span>
              </span>
              <button
                onClick={() => handleRunStep("translate")}
                disabled={runningStep === "translate"}
                className="text-xs text-clay hover:underline hover:text-bronze flex items-center gap-1 font-semibold self-start sm:self-auto"
              >
                <RotateCw size={12} className={runningStep === "translate" ? "animate-spin" : ""} />
                Re-translate Inscription (All Languages)
              </button>
            </div>
          </div>
        ) : (
          <div className="py-10 text-center text-ink/60 space-y-3">
            <RotateCw className="animate-spin text-clay mx-auto" size={24} />
            <p className="text-sm font-serif">Synthesizing multi-language translations from stone carvings...</p>
            <button
              onClick={() => handleRunStep("translate")}
              disabled={runningStep === "translate"}
              className="text-xs bg-clay text-parchment px-4 py-2 rounded-xl hover:bg-bronze transition shadow font-medium"
            >
              {runningStep === "translate" ? "Translating..." : "Translate to Multi-Languages"}
            </button>
          </div>
        )}
      </div>

      {/* HIGHLIGHT 3: SIDE-BY-SIDE INSCRIPTION PHOTO & VISION ENHANCEMENT */}
      {analysis.image && (
        <div className="bg-white/85 border border-ink/10 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-ink/10 pb-3">
            <div className="flex items-center space-x-2.5">
              <ImageIcon className="text-clay" size={22} />
              <h3 className="font-serif font-bold text-lg text-ink">Stone Wall Inscription Imagery</h3>
            </div>
            {analysis.image.filename && (
              <span className="text-xs font-mono text-ink/60 bg-ink/5 px-2.5 py-1 rounded-md self-start sm:self-auto">
                {analysis.image.filename}
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Original Inscription Photo */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase text-ink/70 tracking-wider">
                  Carved Wall / Stone Surface
                </span>
                <span className="text-[11px] text-ink/40 font-mono">Raw Capture</span>
              </div>
              <div className="bg-ink/5 rounded-xl p-2.5 border border-ink/10 flex items-center justify-center min-h-[260px] overflow-hidden group">
                <img
                  src={`/api/analyses/${analysis.id}/image`}
                  alt="Original Inscription on Wall"
                  className="rounded-lg max-h-80 w-full object-contain transition duration-200 group-hover:scale-[1.02]"
                />
              </div>
            </div>

            {/* Processed & Sharpened Vision View */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase text-clay tracking-wider">
                  Vision Contrast & Edge Sharpened
                </span>
                <span className="text-[11px] text-clay/70 font-mono">CLAHE + Denoised</span>
              </div>
              <div className="bg-ink/5 rounded-xl p-2.5 border border-clay/20 flex items-center justify-center min-h-[260px] overflow-hidden group">
                <img
                  src={`/api/analyses/${analysis.id}/processed_image`}
                  alt="Vision Enhanced Inscription"
                  className="rounded-lg max-h-80 w-full object-contain transition duration-200 group-hover:scale-[1.02]"
                  onError={(e) => {
                    // Fallback to original image if processed image not yet saved
                    (e.target as HTMLImageElement).src = `/api/analyses/${analysis.id}/image`;
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* HIGHLIGHT 4: TRANSCRIBED LINES & ROMANIZED TRANSLITERATION */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Carved Glyphs / Transcribed Lines */}
        <div className="bg-white/85 border border-ink/10 rounded-2xl p-6 space-y-4 shadow-sm flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-ink/10 pb-3">
              <div className="flex items-center space-x-2">
                <FileText className="text-clay" size={20} />
                <h3 className="font-serif font-bold text-lg text-ink">Transcribed Carved Lines</h3>
              </div>
              {ocr && (
                <span className="text-xs font-mono font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                  {Math.round(ocr.confidence * 100)}% Conf
                </span>
              )}
            </div>

            {ocr?.text ? (
              <div className="space-y-2">
                <div className="font-mono text-sm bg-ink/5 border border-ink/10 p-4 rounded-xl whitespace-pre-wrap leading-relaxed max-h-64 overflow-y-auto text-ink/90 font-medium select-all">
                  {ocr.text}
                </div>
                <p className="text-[11px] text-ink/50 italic">
                  Exact characters incised into the stone masonry as read by the epigraphic vision model.
                </p>
              </div>
            ) : (
              <p className="text-sm text-ink/50 italic py-4">Carved lines transcription pending...</p>
            )}
          </div>

          <div className="text-[11px] text-ink/40 pt-2 border-t border-ink/10">
            Source: {ocr?.provider || "Paleographic Vision Engine"}
          </div>
        </div>

        {/* Romanized Phonetics & Transliteration */}
        <div className="bg-white/85 border border-ink/10 rounded-2xl p-6 space-y-4 shadow-sm flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-ink/10 pb-3">
              <div className="flex items-center space-x-2">
                <Sparkles className="text-clay" size={20} />
                <h3 className="font-serif font-bold text-lg text-ink">Phonetic Romanization</h3>
              </div>
              <span className="text-xs font-mono text-ink/50 bg-ink/5 px-2 py-0.5 rounded">
                Pronunciation
              </span>
            </div>

            {transliteration ? (
              <div className="space-y-2">
                <div className="font-mono text-sm bg-amber-50/50 border border-amber-200/60 p-4 rounded-xl whitespace-pre-wrap leading-relaxed max-h-64 overflow-y-auto text-ink/85 italic select-all">
                  {transliteration}
                </div>
                <p className="text-[11px] text-ink/50 italic">
                  Phonetic transcription allowing contemporary readers to pronounce the ancient words.
                </p>
              </div>
            ) : reconstruction?.candidates?.[0]?.text ? (
              <div className="space-y-2">
                <div className="font-mono text-sm bg-ink/5 border border-ink/10 p-4 rounded-xl whitespace-pre-wrap leading-relaxed max-h-64 overflow-y-auto text-ink/80">
                  {reconstruction.candidates[0].text}
                </div>
                <p className="text-[11px] text-ink/50 italic">
                  {reconstruction.candidates[0].reason}
                </p>
              </div>
            ) : (
              <p className="text-sm text-ink/50 italic py-4">Phonetic romanization pending...</p>
            )}
          </div>

          <div className="text-[11px] text-ink/40 pt-2 border-t border-ink/10">
            Linguistic Paleography · Historical Phonology
          </div>
        </div>
      </div>

      {/* SCRIPT ALTERNATIVES & EPIGRAPHIC METADATA */}
      {script?.alternatives && script.alternatives.length > 1 && (
        <div className="bg-white/70 border border-ink/10 rounded-2xl p-5 space-y-2 shadow-sm">
          <span className="text-xs font-bold text-ink/60 uppercase tracking-wider block">
            Plausible Paleographic Script Candidates:
          </span>
          <div className="flex flex-wrap gap-2 pt-1">
            {script.alternatives.slice(1).map((alt: any, idx: number) => (
              <div key={idx} className="bg-ink/5 border border-ink/10 px-3 py-1.5 rounded-xl text-xs flex items-center gap-2">
                <span className="font-serif font-semibold text-ink/80">{alt.script}</span>
                <span className="text-clay font-mono font-medium">{Math.round(alt.confidence * 100)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
