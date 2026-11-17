import { Link } from "react-router-dom";
import { ScanSearch, ShieldCheck, Network, BookOpenCheck, Scroll, Languages, ArrowRight } from "lucide-react";

const capabilities = [
  {
    icon: ScanSearch,
    title: "Historical OCR & Restoration",
    body: "Advanced image enhancement, script identification, and OCR specifically tuned for ancient inscriptions and manuscripts.",
  },
  {
    icon: Languages,
    title: "Automated Translation",
    body: "One-click pipeline that processes your image and delivers an English translation — no manual step-by-step clicking.",
  },
  {
    icon: ShieldCheck,
    title: "Evidence-Aware Analysis",
    body: "Every claim is labelled OBSERVED, RECONSTRUCTED, RETRIEVED, or INFERRED — never presented as certain fact.",
  },
  {
    icon: Network,
    title: "Knowledge Graph",
    body: "Extracted entities and relationships are linked into an explorable historical graph for deeper insight.",
  },
  {
    icon: BookOpenCheck,
    title: "Sourced Historical Context",
    body: "Retrieval-augmented context backed by real citations — or an honest 'no source found.'",
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-parchment text-ink">
      {/* Header */}
      <header className="flex justify-between items-center px-8 py-5 border-b border-ink/10">
        <div className="flex items-center gap-2">
          <Scroll size={20} className="text-clay" />
          <span className="font-bold tracking-wide">EPIGRAPH-AI</span>
        </div>
        <nav className="flex gap-6 text-sm items-center">
          <Link to="/about" className="text-ink/70 hover:text-ink transition">About</Link>
          <Link to="/dashboard" className="text-ink/70 hover:text-ink transition font-medium">Dashboard</Link>
          <Link
            to="/analysis/new"
            className="bg-clay text-parchment px-4 py-2 rounded-lg hover:bg-bronze transition shadow-sm font-medium"
          >
            Open App
          </Link>
        </nav>
      </header>

      {/* Hero */}
      <section className="max-w-3xl mx-auto text-center py-28 px-6">
        <div className="inline-flex items-center gap-2 bg-clay/10 text-clay text-xs font-medium px-3 py-1.5 rounded-full mb-6">
          <Scroll size={13} />
          AI-Powered Epigraphy Research Tool
        </div>
        <h1 className="text-4xl md:text-5xl font-serif font-bold mb-5 leading-tight">
          Discover the Past<br />with Artificial Intelligence
        </h1>
        <p className="text-lg text-ink/60 mb-8 max-w-xl mx-auto leading-relaxed">
          Upload an inscription image and get automated analysis, reconstruction, and English translation — all in one click.
        </p>
        <div className="flex justify-center gap-4">
          <Link
            to="/analysis/new"
            className="bg-clay text-parchment px-7 py-3.5 rounded-lg font-medium hover:bg-bronze transition shadow-sm flex items-center gap-2"
          >
            Start Analysis
            <ArrowRight size={16} />
          </Link>
          <Link
            to="/dashboard"
            className="border border-ink/20 px-7 py-3.5 rounded-lg font-medium hover:bg-ink/5 transition"
          >
            Go to Dashboard
          </Link>
        </div>
      </section>

      {/* How It Works — Pipeline */}
      <section className="bg-white/40 border-y border-ink/5 py-16 px-6">
        <div className="max-w-4xl mx-auto text-center mb-10">
          <h2 className="text-2xl font-serif font-bold mb-2">One Upload. Full Pipeline.</h2>
          <p className="text-sm text-ink/60">Upload → Preprocess → Identify Script → OCR → Reconstruct → Translate</p>
        </div>
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
          {["Upload Image", "Vision Filters", "Script Detection", "OCR", "Reconstruction", "English Translation"].map((step, i) => (
            <div key={step} className="flex items-center gap-3">
              <div className="bg-clay/10 border border-clay/20 rounded-xl px-4 py-3 text-center min-w-[120px]">
                <span className="text-xs font-bold text-clay block mb-0.5">Step {i + 1}</span>
                <span className="text-xs text-ink/80 font-medium">{step}</span>
              </div>
              {i < 5 && <ArrowRight size={14} className="text-ink/20 hidden md:block" />}
            </div>
          ))}
        </div>
      </section>

      {/* Capabilities Grid */}
      <section id="how-it-works" className="max-w-5xl mx-auto grid md:grid-cols-2 lg:grid-cols-3 gap-5 px-6 py-20">
        {capabilities.map(({ icon: Icon, title, body }) => (
          <div key={title} className="border border-ink/10 rounded-xl p-6 bg-white/50 hover:shadow-md transition group">
            <div className="w-10 h-10 rounded-lg bg-clay/10 flex items-center justify-center mb-4 group-hover:bg-clay/20 transition">
              <Icon size={20} className="text-clay" />
            </div>
            <h3 className="font-semibold mb-1.5 text-ink">{title}</h3>
            <p className="text-sm text-ink/60 leading-relaxed">{body}</p>
          </div>
        ))}
      </section>

      {/* Responsible AI Footer */}
      <section className="bg-ink text-parchment px-6 py-14 text-center">
        <Scroll size={24} className="mx-auto mb-3 text-bronze" />
        <h2 className="font-serif text-2xl mb-3">Responsible AI for Scholarship</h2>
        <p className="max-w-2xl mx-auto text-sm text-parchment/70 leading-relaxed">
          EPIGRAPH-AI never claims to have determined historical truth with certainty.
          Reconstruction is probabilistic, translation can be uncertain, and sources can disagree.
          Every AI-generated interpretation requires expert validation.
        </p>
        <p className="text-xs text-parchment/40 mt-6">© 2026 EPIGRAPH-AI · Built for researchers, by researchers.</p>
      </section>
    </div>
  );
}
