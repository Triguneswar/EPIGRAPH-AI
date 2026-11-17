"""
AI-assisted text reconstruction provider abstraction.

CRITICAL invariant enforced throughout this module: reconstruction NEVER
overwrites the observed OCR text. It only ever proposes ranked candidates
alongside it, each carrying a confidence/model-score and a reason, and the
result is always flagged `requires_expert_verification=True`.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ReconstructionCandidate:
    text: str
    confidence: float
    reason: str


@dataclass
class ReconstructionResult:
    observed_text: str
    candidates: list[ReconstructionCandidate] = field(default_factory=list)
    provider: str = "unset"
    requires_expert_verification: bool = True


UNCERTAIN_MARKER = re.compile(r"\[\?\]|_+")


class ReconstructionProvider(ABC):
    @abstractmethod
    def reconstruct(self, observed_text: str, context: str = "") -> ReconstructionResult:
        raise NotImplementedError


class LexiconLLMReconstructionProvider(ReconstructionProvider):
    """
    Real provider: combines a historical-vocabulary lookup with an LLM
    (via app.rag.llm_provider) to propose ranked fill candidates for masked
    spans. Requires an LLM provider to be configured (LLM_PROVIDER != demo).
    """

    def __init__(self, llm_client, vocabulary: list[str] | None = None):
        self.llm_client = llm_client
        self.vocabulary = vocabulary or []

    def reconstruct(self, observed_text: str, context: str = "") -> ReconstructionResult:
        if not UNCERTAIN_MARKER.search(observed_text):
            # nothing to reconstruct
            return ReconstructionResult(
                observed_text=observed_text, candidates=[], provider="lexicon_llm",
                requires_expert_verification=False,
            )

        prompt = (
            "You are assisting with historical epigraphy. Given an OCR "
            "transcription with uncertain spans marked as [?] or underscores, "
            "propose up to 3 plausible completions using historical vocabulary "
            "and the surrounding context. Return ONLY a JSON array of "
            '{"text":..., "confidence":0-1, "reason":...}. Never claim certainty.\n\n'
            f"Observed text: {observed_text}\nContext: {context}\n"
            f"Known vocabulary sample: {', '.join(self.vocabulary[:50])}"
        )
        raw = self.llm_client.complete(prompt)
        import json

        try:
            parsed = json.loads(raw)
            candidates = [
                ReconstructionCandidate(c["text"], float(c["confidence"]), c["reason"]) for c in parsed
            ]
        except Exception:
            candidates = []

        return ReconstructionResult(
            observed_text=observed_text,
            candidates=candidates,
            provider="lexicon_llm",
            requires_expert_verification=True,
        )


class DemoReconstructionProvider(ReconstructionProvider):
    """DEMO/FALLBACK MODE. Does not invent historical text. If uncertain
    spans exist, it explains that reconstruction requires a configured LLM
    provider, rather than pretending to have proposed a real candidate."""

    def reconstruct(self, observed_text: str, context: str = "") -> ReconstructionResult:
        if not UNCERTAIN_MARKER.search(observed_text):
            return ReconstructionResult(
                observed_text=observed_text, candidates=[], provider="demo",
                requires_expert_verification=False,
            )

        return ReconstructionResult(
            observed_text=observed_text,
            candidates=[
                ReconstructionCandidate(
                    text="[DEMO MODE — configure LLM_PROVIDER to generate real "
                    "reconstruction candidates for this uncertain span.]",
                    confidence=0.0,
                    reason="No reconstruction model/LLM configured.",
                )
            ],
            provider="demo (no real reconstruction performed)",
            requires_expert_verification=True,
        )


def get_reconstruction_provider(use_demo: bool = True, llm_client=None) -> ReconstructionProvider:
    if not use_demo and llm_client is not None:
        return LexiconLLMReconstructionProvider(llm_client)
    return DemoReconstructionProvider()
