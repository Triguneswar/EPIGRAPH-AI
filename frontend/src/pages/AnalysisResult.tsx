import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getAnalysis, runPipeline, runStep } from "../services/api";
import { Play, RotateCw, CheckCircle2, AlertTriangle, Languages, FileText, Image as ImageIcon, Sparkles } from "lucide-react";

export default function AnalysisResult() {
  const { id } = useParams<{ id: string }>();
  const [analysis, setAnalysis] = useState<any>(null);
  const [running, setRunning] = useState<boolean>(false);
  const [runningStep, setRunningStep] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    if (!id) return;
    try {
      const data = await getAnalysis(id);
      setAnalysis(data);
      // If status is uploaded and no results yet, run full pipeline automatically!
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

  if (!analysis) {
    return (
      <div className="flex items-center space-x-3 text-ink/70 py-12">
        <RotateCw className="animate-spin text-clay" size={20} />
        <span>Loading EPIGRAPH-AI analysis...</span>
      </div>
    );
  }

  const translation = analysis.translation;
  const script = analysis.script_prediction;
  const ocr = analysis.ocr_result;
  const reconstruction = analysis.reconstruction;
  const preprocess = analysis.preprocessing;
  const isComplete = Boolean(translation && ocr);

  return (
    <div className="max-w-4xl space-y-6 pb-12">
      {/* Top Title and Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-ink/10 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-serif font-bold text-ink">
              EPIGRAPH-AI Analysis
            </h1>
            <span className="text-xs px-2.5 py-0.5 rounded-full font-mono font-medium bg-clay/10 text-clay">
              {analysis.id.slice(0, 8)}
            </span>
          </div>
          <div className="flex items-center space-x-2 mt-1">
            <span className="text-xs font-semibold uppercase tracking-wider text-ink/50">Status:</span>
            {isComplete ? (
              <span className="inline-flex items-center text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                <CheckCircle2 size={13} className="mr-1" /> Complete
              </span>
            ) : (
              <span className="text-xs font-medium text-amber-700 bg-amber-50 px-2 py-0.5 rounded">
                {analysis.status}
              </span>
            )}
          </div>
        </div>

        {/* Master Run All Button */}
        <div className="flex items-center space-x-3">
          <Link
            to="/new"
            className="text-xs text-ink/70 hover:text-ink px-3 py-2 rounded-md border border-ink/15 hover:bg-white/60 transition"
          >
            Upload New
          </Link>
          <button
            onClick={handleRunAll}
            disabled={running}
            className="flex items-center space-x-2 text-sm bg-clay hover:bg-bronze text-parchment font-medium px-4 py-2 rounded-lg shadow-sm transition disabled:opacity-50"
          >
            {running ? (
              <>
                <RotateCw size={16} className="animate-spin" />
                <span>Processing Pipeline...</span>
              </>
            ) : (
              <>
                <Sparkles size={16} />
                <span>{isComplete ? "Re-run Full Analysis" : "Run All Steps At Once"}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg flex items-center space-x-2">
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* 1. ENGLISH TRANSLATION (PROMINENT AT TOP) */}
      <div className="bg-gradient-to-br from-amber-50 via-white to-orange-50/50 border-2 border-amber-300/80 rounded-2xl p-6 shadow-md space-y-4">
        <div className="flex items-center justify-between border-b border-amber-200/60 pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-lg bg-clay/15 flex items-center justify-center text-clay">
              <Languages size={22} />
            </div>
            <div>
              <h2 className="font-serif font-bold text-xl text-ink">English Translation</h2>
              <p className="text-xs text-ink/50">Scholarly paleographic and contextual translation</p>
            </div>
          </div>
          {translation && (
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800">
                {(translation.confidence * 100).toFixed(0)}% Confidence
              </span>
            </div>
          )}
        </div>

        {translation ? (
          <div className="space-y-4 pt-1">
            <div className="bg-white border border-amber-200 rounded-xl p-5 shadow-sm">
              <p className="text-base md:text-lg text-ink font-serif leading-relaxed italic text-ink/90">
                "{translation.english}"
              </p>
            </div>

            {translation.modern_tamil && (
              <div className="bg-amber-50/70 border border-amber-200/80 rounded-xl p-4">
                <p className="text-xs font-bold text-clay uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <span>🏛️</span> Regional Historical Interpretation (Tamil / Vernacular):
                </p>
                <p className="text-base text-ink/90 leading-relaxed font-tamil font-normal tracking-wide">
                  {translation.modern_tamil}
                </p>
              </div>
            )}

            <div className="flex items-center justify-between text-xs text-ink/50 pt-1">
              <span>Engine: <span className="font-mono text-clay">{translation.provider}</span></span>
              <button
                onClick={() => handleRunStep("translate")}
                disabled={runningStep === "translate"}
                className="text-xs text-clay hover:underline hover:text-bronze flex items-center gap-1"
              >
                <RotateCw size={12} className={runningStep === "translate" ? "animate-spin" : ""} />
                Re-translate
              </button>
            </div>
          </div>
        ) : (
          <div className="py-6 text-center text-ink/60 space-y-2">
            <p className="text-sm">English translation will appear automatically once pipeline runs.</p>
            <button
              onClick={() => handleRunStep("translate")}
              disabled={runningStep === "translate"}
              className="text-xs bg-clay text-parchment px-4 py-2 rounded-lg hover:bg-bronze transition disabled:opacity-50"
            >
              {runningStep === "translate" ? "Translating..." : "Translate to English"}
            </button>
          </div>
        )}
      </div>

      {/* Grid of Inscription Analysis Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* 2. SCRIPT IDENTIFICATION */}
        <div className="bg-white/70 border border-ink/10 rounded-xl p-5 space-y-3 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <FileText className="text-clay" size={18} />
              <h3 className="font-serif font-semibold text-ink">Script Identification</h3>
            </div>
            {script && (
              <span className="text-xs font-mono font-medium text-ink/60 bg-ink/5 px-2 py-0.5 rounded">
                {(script.confidence * 100).toFixed(0)}%
              </span>
            )}
          </div>

          {script ? (
            <div className="space-y-3">
              <div>
                <span className="text-xs text-ink/50 uppercase font-semibold">Identified Script:</span>
                <p className="text-xl font-bold font-serif text-clay mt-0.5">{script.script}</p>
              </div>

              {script.alternatives && script.alternatives.length > 0 && (
                <div>
                  <span className="text-xs text-ink/50 uppercase font-semibold">Alternative Candidates:</span>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {script.alternatives.map((alt: any, idx: number) => (
                      <span key={idx} className="text-xs bg-ink/5 text-ink/80 px-2 py-1 rounded">
                        {alt.script} ({(alt.confidence * 100).toFixed(0)}%)
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <p className="text-xs text-ink/50 pt-1">Provider: {script.provider}</p>
            </div>
          ) : (
            <p className="text-sm text-ink/50 italic py-2">Script not identified yet.</p>
          )}
        </div>

        {/* 3. OCR OBSERVED TEXT */}
        <div className="bg-white/70 border border-ink/10 rounded-xl p-5 space-y-3 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Sparkles className="text-clay" size={18} />
              <h3 className="font-serif font-semibold text-ink">OCR Observed Text</h3>
            </div>
            {ocr && (
              <span className="text-xs font-mono font-medium text-ink/60 bg-ink/5 px-2 py-0.5 rounded">
                {(ocr.confidence * 100).toFixed(0)}% Conf
              </span>
            )}
          </div>

          {ocr ? (
            <div className="space-y-2">
              <div className="font-mono text-sm bg-ink/5 border border-ink/10 p-3 rounded-lg whitespace-pre-wrap max-h-40 overflow-y-auto">
                {ocr.text}
              </div>
              <p className="text-xs text-ink/50">Provider: {ocr.provider}</p>
            </div>
          ) : (
            <p className="text-sm text-ink/50 italic py-2">OCR transcription pending.</p>
          )}
        </div>
      </div>

      {/* 4. AI-ASSISTED RECONSTRUCTION */}
      <div className="bg-white/70 border border-ink/10 rounded-xl p-5 space-y-3 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="text-clay" size={18} />
            <h3 className="font-serif font-semibold text-ink">AI-Assisted Reconstruction</h3>
          </div>
          {reconstruction?.requires_expert_verification && (
            <span className="text-xs text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded flex items-center gap-1">
              <AlertTriangle size={12} /> Requires Expert Verification
            </span>
          )}
        </div>

        <p className="text-xs text-ink/50">
          EPIGRAPH-AI invariant: Observed OCR text is strictly preserved and never overwritten by reconstructed guesses.
        </p>

        {reconstruction ? (
          <div>
            {reconstruction.candidates && reconstruction.candidates.length > 0 ? (
              <ul className="space-y-2 mt-2">
                {reconstruction.candidates.map((c: any, i: number) => (
                  <li key={i} className="text-sm border border-ink/10 rounded-lg p-3 bg-white/50">
                    <div className="flex justify-between items-center mb-1">
                      <strong className="text-clay font-mono">{c.text}</strong>
                      <span className="text-xs font-mono bg-ink/5 px-1.5 py-0.5 rounded">
                        {(c.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-xs text-ink/60">{c.reason}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-ink/60 bg-ink/5 p-3 rounded-lg">
                No uncertain or damaged spans detected in observed text — reconstruction preserved as recorded.
              </p>
            )}
          </div>
        ) : (
          <p className="text-sm text-ink/50 italic py-2">Reconstruction pending.</p>
        )}
      </div>

      {/* 5. PREPROCESSED IMAGE & QUALITY METRICS */}
      <div className="bg-white/70 border border-ink/10 rounded-xl p-5 space-y-3 shadow-sm">
        <div className="flex items-center space-x-2">
          <ImageIcon className="text-clay" size={18} />
          <h3 className="font-serif font-semibold text-ink">Image Preprocessing & Vision Filters</h3>
        </div>

        {preprocess ? (
          <div className="space-y-2">
            <div className="flex flex-wrap gap-1.5">
              {preprocess.steps_applied?.map((step: string, idx: number) => (
                <span key={idx} className="text-xs bg-clay/10 text-clay font-medium px-2.5 py-1 rounded-md">
                  ✓ {step.replace(/_/g, " ")}
                </span>
              ))}
            </div>
            {preprocess.enhancement_metadata && (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs text-ink/70 bg-ink/5 p-3 rounded-lg mt-2">
                <div>
                  <span className="text-ink/40 block">Resolution:</span>
                  <span className="font-mono font-medium">{preprocess.enhancement_metadata.processed_resolution}</span>
                </div>
                <div>
                  <span className="text-ink/40 block">Sharpness Score:</span>
                  <span className="font-mono font-medium">{preprocess.enhancement_metadata.blur_score_after}</span>
                </div>
                <div>
                  <span className="text-ink/40 block">Quality Status:</span>
                  <span className="font-medium text-emerald-700 capitalize">{preprocess.enhancement_metadata.image_quality_flag}</span>
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-ink/50 italic py-2">Image preprocessing pending.</p>
        )}
      </div>
    </div>
  );
}
