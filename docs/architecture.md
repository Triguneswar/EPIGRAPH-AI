# Architecture

## Workflow

```
Upload → Validate → Preprocess (OpenCV) → Script ID → OCR →
Damaged-region detection → Reconstruction (candidates, never overwrite OCR) →
Translation → RAG retrieval → Entity extraction → Knowledge graph →
Verification (evidence status + conflicts) → PDF report
```

## Agent design (LangGraph — interface defined, orchestration to be wired
once LLM/network access is configured)

Supervisor → Vision → Script → OCR → Reconstruction → Translation →
Research (RAG) → Entity → Knowledge Graph → Verification → Report.

The Supervisor decision rules (implemented as conditional edges once
LangGraph is wired):
- image quality poor → re-run preprocessing
- OCR confidence low → trigger reconstruction
- historical evidence insufficient → expand RAG search
- sources conflict → flag conflict, do not silently choose
- confidence low → require human verification

## Evidence status taxonomy

`OBSERVED | OCR | RECONSTRUCTED | RETRIEVED | INFERRED | UNCERTAIN`
— implemented in `backend/app/verification/engine.py`.

## Database schema (SQLAlchemy — `backend/app/models/models.py`)

`users, analyses, images, preprocessing_results, script_predictions,
ocr_results, reconstruction_results, translations, historical_entities,
sources, analysis_sources, verification_results, reports`

## Knowledge graph schema (Neo4j)

```
(:Person)-[:BELONGS_TO]->(:Dynasty)
(:Person)-[:ASSOCIATED_WITH]->(:Temple)
(:Person)-[:RULED]->(:Region)
(:Inscription)-[:FOUND_AT]->(:Place)
(:Inscription)-[:MENTIONS]->(:Person)
(:Inscription)-[:DATED_TO]->(:Period)
```

## API routes

```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me

POST   /api/analyses                    (multipart upload)
GET    /api/analyses
GET    /api/analyses/{id}
DELETE /api/analyses/{id}

POST   /api/analyses/{id}/preprocess
POST   /api/analyses/{id}/script
POST   /api/analyses/{id}/ocr
POST   /api/analyses/{id}/reconstruct
```

Additional routes (`translate`, `research`, `entities`, `graph`, `verify`,
`report`, `/api/rag/*`) follow the same pattern as the four implemented
above and are the natural next extension — each needs a configured
LLM/embedding/Neo4j backend to produce real (non-demo) output.

## Provider abstraction pattern (used throughout)

```python
class SomeProvider(ABC):
    @abstractmethod
    def do_the_thing(self, ...): ...

class RealProvider(SomeProvider): ...   # requires model/API/network
class DemoProvider(SomeProvider): ...   # always available, clearly labelled

def get_provider(use_demo=True):
    if not use_demo:
        try:
            return RealProvider()
        except (FileNotFoundError, ImportError):
            pass
    return DemoProvider()
```
This is implemented for script classification, OCR, reconstruction, and the
LLM client — and is the pattern to follow when adding translation/embedding
providers.
