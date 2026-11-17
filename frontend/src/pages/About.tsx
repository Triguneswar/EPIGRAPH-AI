import { Link } from "react-router-dom";

export default function About() {
  return (
    <div className="min-h-screen bg-parchment text-ink px-6 py-16">
      <div className="max-w-2xl mx-auto space-y-6">
        <Link to="/" className="text-sm text-clay">&larr; Back</Link>
        <h1 className="text-3xl font-serif font-semibold">About This Project</h1>

        <section>
          <h2 className="font-semibold mb-1">Motivation</h2>
          <p className="text-sm text-ink/70">
            Historical inscriptions and manuscripts are difficult to read,
            translate, and contextualize — especially when damaged or written
            in less-documented scripts. This project explores how a
            multimodal, evidence-aware AI pipeline can assist (not replace)
            human epigraphers and historians.
          </p>
        </section>

        <section>
          <h2 className="font-semibold mb-1">Approach</h2>
          <p className="text-sm text-ink/70">
            Image restoration, script identification, historical OCR,
            damage-aware reconstruction, translation, retrieval-augmented
            historical context, entity extraction, and a knowledge graph —
            orchestrated by a supervised agent workflow, with every output
            explicitly labelled OBSERVED, RECONSTRUCTED, RETRIEVED, or
            INFERRED.
          </p>
        </section>

        <section>
          <h2 className="font-semibold mb-1">Responsible AI</h2>
          <p className="text-sm text-ink/70">
            OCR may contain errors. Scripts can be ambiguous. Reconstruction
            is probabilistic. Sources can disagree. This system never claims
            to determine historical truth with certainty — all
            interpretations require expert validation.
          </p>
        </section>
      </div>
    </div>
  );
}
