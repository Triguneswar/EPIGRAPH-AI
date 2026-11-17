# EPIGRAPH-AI

<div align="center">

![EPIGRAPH-AI Banner](https://img.shields.io/badge/EPIGRAPH--AI-Multimodal%20Epigraphic%20Vision-8B4513?style=for-the-badge)

**Autonomous AI Vision & Multilingual Decipherment Platform for Ancient Stone Wall Literature, Temple Epigraphs, Inscribed Steles, and Historical Manuscripts**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6.2-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org)
[![Vite](https://img.shields.io/badge/Vite-5.4.7-646CFF?style=flat-square&logo=vite)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.10.0-5C3EE8?style=flat-square&logo=opencv)](https://opencv.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4.13-06B6D4?style=flat-square&logo=tailwindcss)](https://tailwindcss.com)
[![Gemini Vision](https://img.shields.io/badge/Google%20Gemini-Multimodal%20Vision-4285F4?style=flat-square&logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-amber?style=flat-square)](LICENSE)

[Key Features](#key-features) • [Multilingual Suite](#multilingual-translation-suite) • [Architecture](#system-architecture) • [Getting Started](#getting-started) • [API Reference](#api-reference) • [Evidence Taxonomy](#archaeological-evidence-taxonomy)

</div>

---

## Overview

Ancient inscriptions carved into stone masonry, granite temple walls, cave sanctuaries, and memorial steles represent the primary physical records of human civilizations. However, standard OCR models fail completely when applied to raw field photography due to:
- Deep 3D chiseled grooves with irregular lighting, shadows, and chalk marks.
- Severe atmospheric weathering, erosion, lichen growth, and damaged stone spans.
- Archaic, extinct scripts (Old Tamil, Grantha, Vatteluttu, Tamil-Brahmi, Nagari, Classical Latin, Ancient Greek) with complex ligatures.

**EPIGRAPH-AI** solves this challenge through an end-to-end, multi-stage archaeological intelligence pipeline. By combining adaptive computer-vision enhancement (CLAHE, bilateral denoising, morphometric contour analysis) with advanced Multimodal Vision AI, the platform directly deciphers stone inscriptions from photographs, transcribes carved glyphs, reconstructs damaged lines, and synthesizes authentic scholarly translations simultaneously across **English, Hindi, Tamil, Telugu, Kannada, and Regional Vernacular**.

---

## Key Features

| Capability | Description | Core Engine / Module |
| :--- | :--- | :--- |
| **Direct Photo Decipherment** | Deciphers raw camera photos of temple walls, rock faces, and steles without manual transcription. | `EpigraphVisionEngine` |
| **Adaptive Vision Filtering** | CLAHE (Contrast Limited Adaptive Histogram Equalization) and Bilateral edge-preserving filtering. | `backend/app/vision/preprocessing.py` |
| **Paleographic Script Identification** | Detects ancient script family, historical era, regnal period, and dynastic lineage with confidence scoring. | `backend/app/ai/script_classifier.py` |
| **Carved Character Transcription** | Line-by-line transcription of incised characters in normalized Unicode and historical orthography. | `backend/app/ocr/providers.py` |
| **Phonetic Romanization** | Pronunciation guide transliterating archaic characters into Latin phonetics for modern researchers. | `backend/app/ocr/providers.py` |
| **Damage-Aware Reconstruction** | Identifies weathered/eroded character spans and proposes bracketed scholarly reconstructions `[text]`. | `backend/app/reconstruction/providers.py` |
| **Multilingual Literature Suite** | Instant translations across 6 language channels (English, Hindi, Tamil, Telugu, Kannada, Vernacular). | `backend/app/translation/providers.py` |
| **Historical Entity Extraction** | Automatically classifies Kings, Deities, Temples, Land Grants, Village Assemblies, and Measures. | `backend/app/models/models.py` |
| **Zero-Key Offline Fallback** | Adaptive OpenCV morphometry analyzes continuous headstrokes (Shirorekha) and Dravidian circularities offline. | `EpigraphVisionEngine._run_adaptive_local_vision` |

---

## Multilingual Translation Suite

Rather than restricting regional readings to a single dialect, EPIGRAPH-AI translates ancient literature into comprehensive, scholarly modern prose across multiple languages:

| Language | Script | Representation in UI | Primary Purpose & Scope |
| :--- | :--- | :---: | :--- |
| **English** | Latin | `🇬🇧 English` | Primary scholarly translation detailing monarchs, regnal years, endowments, and decrees. |
| **Hindi (`हिन्दी`)** | Devanagari | `🇮🇳 हिन्दी` | Comprehensive modern Hindi translation (सम्पूर्ण आधुनिक हिन्दी अनुवाद) of the inscription. |
| **Tamil (`தமிழ்`)** | Tamil | `🏛️ தமிழ்` | Classical & modern Tamil interpretation (முழுமையான நவீன தமிழ் உரை விளக்கம்). |
| **Telugu (`తెలుగు`)** | Telugu | `🇮🇳 తెలుగు` | Natural modern Telugu translation (పూర్తి ఆధునిక తెలుగు అనువాదం) for epigraphic analysis. |
| **Kannada (`ಕನ್ನಡ`)** | Kannada | `🇮🇳 ಕನ್ನಡ` | Authentic modern Kannada translation (ಸಂಪೂರ್ಣ ಆಧುನಿಕ ಕನ್ನಡ ಅನುವಾದ). |
| **Vernacular** | Regional | `🌐 Vernacular` | Historical vernacular reading matching the specific epigraphic culture of the site. |

The frontend provides **interactive language tabs** and **side-by-side comparative cards** with one-click copy buttons for every language.

---

## Supported Scripts & Historical Eras

EPIGRAPH-AI specializes in South Asian and classical worldwide epigraphy:

| Script Family | Target Historical Era | Primary Region / Monuments |
| :--- | :--- | :--- |
| **Tamil-Grantha** | 7th – 14th Century CE | Brihadisvara Temple (Thanjavur), Gangaikonda Cholapuram, Kanchipuram |
| **Old / Medieval Tamil** | 8th – 13th Century CE | Chola, Pandya, and Chera imperial temple wall edicts |
| **Vatteluttu** | 5th – 11th Century CE | Kongu Nadu, Madurai rock inscriptions, Kerala copper plates |
| **Tamil-Brahmi** | 3rd Century BCE – 3rd Century CE | Mangulam, Sittannavasal, Pugalur natural rock caverns |
| **Devanagari / Nagari** | 8th – 16th Century CE | North & Central Indian stone slabs, Rashtrakuta, Pratihara, Paramara |
| **Telugu-Kannada (Halegannada)** | 5th – 14th Century CE | Kadamba, Chalukya, Hoysala, Kakatiya, and Vijayanagara inscriptions |
| **Classical Latin** | 1st Century BCE – 4th Century CE | Roman monumental lapidary inscriptions, triumphal arches, steles |
| **Ancient Greek** | 5th Century BCE – 2nd Century CE | Epigraphic decrees, boundary stones, public dedication slabs |

---

## System Architecture

```
                       [ Input Stone Photo / Capture ]
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │    Adaptive Preprocessing     │
                      │  - CLAHE Dynamic Contrast     │
                      │  - Bilateral Edge-Smoothing   │
                      │  - Otsu Polarity Threshold    │
                      └───────────────┬───────────────┘
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │   Epigraph Vision Engine      │
                      │  (Google Gemini / Claude /    │
                      │   OpenAI / Local Ollama)      │
                      └───────────────┬───────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
         ▼                            ▼                            ▼
┌──────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│ Script & Dynasty │        │ Character OCR &  │        │ Damaged Span     │
│ Identification   │        │ Phonetic Latin   │        │ Scholarly        │
│ & Era Dating     │        │ Transliteration  │        │ Reconstruction   │
└────────┬─────────┘        └────────┬─────────┘        └────────┬─────────┘
         │                            │                            │
         └────────────────────────────┼────────────────────────────┘
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │  Multilingual Synthesis Engine│
                      │  - 🇬🇧 English Master Reading  │
                      │  - 🇮🇳 Hindi (हिन्दी अनुवाद)   │
                      │  - 🏛️ Tamil (தமிழ் உரை)       │
                      │  - 🇮🇳 Telugu (తెలుగు అనువాదం) │
                      │  - 🇮🇳 Kannada (ಕನ್ನಡ ಅನುವಾದ) │
                      │  - 🌐 Cultural Vernacular     │
                      └───────────────┬───────────────┘
                                      │
                                      ▼
                      ┌───────────────────────────────┐
                      │   Entity & Knowledge Graph    │
                      │  Rulers • Deities • Temples   │
                      │  Endowments • Land Grants     │
                      └───────────────────────────────┘
```

---

## Directory Structure

```
EPIGRAPH-AI/
├── .env.example                       # Reference environment variables
├── .gitignore                         # Strict exclusion for keys, DBs, and venvs
├── docker-compose.yml                 # Optional container orchestration
├── start_all.bat                      # One-click master launcher (Backend + Frontend)
├── start_backend.bat                  # Dedicated backend launcher (Port 8000)
├── start_frontend.bat                 # Dedicated frontend launcher (Port 5173)
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   ├── epigraph_vision_engine.py  # Core Multimodal AI Vision & local CV engine
│   │   │   └── script_classifier.py       # Script identification provider
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── analyses.py            # End-to-end analysis & pipeline endpoints
│   │   │       ├── auth.py                # Authentication & user sessions
│   │   │       └── settings.py            # Dynamic AI Vision API key configuration
│   │   ├── core/
│   │   │   ├── config.py                  # Pydantic environment configuration
│   │   │   └── security.py                # Password hashing & JWT handling
│   │   ├── db/
│   │   │   └── session.py                 # SQLite / PostgreSQL SQLAlchemy engine
│   │   ├── models/
│   │   │   └── models.py                  # Database entities (Analyses, Translations, Entities)
│   │   ├── ocr/
│   │   │   └── providers.py               # Line transcription & phonetics
│   │   ├── reconstruction/
│   │   │   └── providers.py               # Scholarly text reconstruction
│   │   ├── schemas/
│   │   │   └── schemas.py                 # Pydantic schemas (TranslationOut, AnalysisOut)
│   │   ├── translation/
│   │   │   └── providers.py               # Multi-language translation integration
│   │   ├── verification/
│   │   │   └── engine.py                  # Evidence classification & conflicts
│   │   ├── vision/
│   │   │   └── preprocessing.py           # CLAHE, Bilateral & morphological filters
│   │   └── main.py                        # FastAPI application entrypoint
│   └── requirements.txt                   # Backend Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/                    # Modular UI components
│   │   ├── layouts/
│   │   │   └── AppLayout.tsx              # Navigation bar, header, and connection status
│   │   ├── pages/
│   │   │   ├── AnalysisResult.tsx         # Interactive Multi-Language Reading Suite
│   │   │   ├── Dashboard.tsx              # Analysis catalog and overview
│   │   │   ├── Landing.tsx                # Public showcase & marketing page
│   │   │   ├── Login.tsx / Register.tsx   # User authentication screens
│   │   │   └── NewAnalysis.tsx            # Drag-and-drop photo upload & live decipherment
│   │   ├── services/
│   │   │   └── api.ts                     # Axios API client
│   │   ├── App.tsx                        # React Router configuration
│   │   └── main.tsx                       # React DOM entrypoint
│   ├── package.json                       # Frontend npm dependencies
│   ├── vite.config.ts                     # Vite build & proxy config
│   └── tailwind.config.js                 # Earthy parchment/clay theme config
└── docs/
    ├── architecture.md                    # Detailed pipeline specification
    └── datasets.md                        # Dataset guidelines & evaluation protocols
```

---

## Supported Multimodal AI Vision Providers

EPIGRAPH-AI connects with leading multimodal APIs as well as fully offline local engines:

| Provider | Recommended Model | Free Tier Available? | Setup Method |
| :--- | :--- | :---: | :--- |
| **Google Gemini (Default)** | `gemini-flash-lite-latest`<br>`gemini-3.8-flash` | **Yes** (No credit card needed) | Enter key starting with `AIzaSy...` in web UI or `.env`. |
| **OpenAI / Compatible** | `gpt-4o`<br>`gpt-4o-mini` | No (Paid API) | Enter key starting with `sk-...` in web UI or `.env`. |
| **Anthropic Claude** | `claude-3-5-sonnet-20241022` | No (Paid API) | Enter key starting with `sk-ant...` in web UI or `.env`. |
| **Local Ollama (Offline)** | `llama3.2-vision`<br>`qwen2.5-vl` | **100% Free & Local** | Run `ollama run llama3.2-vision` locally on port 11434. |
| **Adaptive Local CV** | Geometric Contour Engine | **100% Offline** | Built-in zero-configuration morphological analyzer. |

---

## Getting Started

### Prerequisites

- **Python**: Version `3.11` or higher
- **Node.js**: Version `18.x` or higher (with `npm`)
- **Git**: Installed and accessible on PATH

---

### Method 1: One-Click Windows Launch (Recommended)

1. Clone or download the repository:
   ```powershell
   git clone https://github.com/Triguneswar/EPIGRAPH-AI.git
   cd EPIGRAPH-AI
   ```
2. Double-click `start_all.bat` (or run it in PowerShell):
   ```powershell
   .\start_all.bat
   ```
   This opens two terminal windows:
   - **Backend**: Running FastAPI on [http://localhost:8000](http://localhost:8000)
   - **Frontend**: Running Vite React on [http://localhost:5173](http://localhost:5173)
3. Open your browser to [http://localhost:5173](http://localhost:5173).

---

### Method 2: Manual Installation

#### 1. Backend Setup

```bash
cd backend

# Create and activate Python virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory (or copy from `.env.example`):
```env
APP_NAME=EPIGRAPH-AI
ENVIRONMENT=development
DATABASE_URL=sqlite:///./digital_archaeologist.db

# Live Multimodal AI Key (Get a free key at https://aistudio.google.com)
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere
LLM_MODEL=gemini-flash-lite-latest

USE_DEMO_PROVIDERS=false
```

Start the backend server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup

In a new terminal window:
```bash
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173).

---

## Configuration Reference

All settings can be configured via `.env` in the root or `backend/` directory:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `gemini` | AI vision provider (`gemini`, `openai_compatible`, `claude`, `local`). |
| `GEMINI_API_KEY` | `""` | Google Gemini API key (starts with `AIzaSy...`). |
| `LLM_MODEL` | `gemini-flash-lite-latest` | Multimodal model name (`gemini-flash-lite-latest`, `gemini-3.8-flash`, `gpt-4o`). |
| `DATABASE_URL` | `sqlite:///./digital_archaeologist.db` | SQLite database path or PostgreSQL connection string. |
| `MAX_UPLOAD_SIZE_MB` | `25` | Maximum upload size for stone inscription photography (in MB). |
| `USE_DEMO_PROVIDERS` | `false` | When `false`, executes live vision & paleographic analysis. |
| `JWT_SECRET` | `CHANGE_ME_DEV...` | Secret key used to sign session authorization tokens. |

---

## API Reference

The FastAPI server provides automated Swagger interactive documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

### Core Inscription Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/analyses` | Uploads an inscription image (multipart/form-data) and initializes record. |
| `POST` | `/api/analyses/{id}/pipeline` | **One-Click Master Pipeline**: Runs Preprocessing → Vision AI → Script ID → OCR → Reconstruction → Multi-Language Translation. |
| `GET` | `/api/analyses/{id}` | Fetches complete analysis record including all multilingual translations. |
| `POST` | `/api/analyses/{id}/preprocess` | Runs OpenCV CLAHE and bilateral filtering. |
| `POST` | `/api/analyses/{id}/script` | Identifies ancient script family and historical era. |
| `POST` | `/api/analyses/{id}/ocr` | Transcribes visible carved characters and phonetics. |
| `POST` | `/api/analyses/{id}/reconstruct` | Synthesizes damage-aware scholarly reconstructions `[text]`. |
| `POST` | `/api/analyses/{id}/translate` | Generates translations across English, Hindi, Tamil, Telugu, and Kannada. |
| `POST` | `/api/settings` | Updates active AI Vision API keys dynamically from the web UI. |
| `POST` | `/api/settings/test` | Verifies API key validity directly against the provider. |

---

## Archaeological Evidence Taxonomy

To maintain strict scientific and epigraphic rigor, EPIGRAPH-AI enforces a transparent evidence taxonomy implemented in `backend/app/verification/engine.py`:

```
   [ PHYSICAL EVIDENCE ]
           │
           ├── OBSERVED      ── Direct visible strokes identified on stone masonry
           ├── OCR           ── Mechanically transcribed character glyphs
           │
   [ SCHOLARLY INFERENCE ]
           │
           ├── RECONSTRUCTED ── Restored eroded spans denoted in scholarly brackets [ ]
           ├── RETRIEVED     ── Cross-referenced against historical corpus & gazetteers
           ├── INFERRED      ── Contextual deduction based on regnal dates and dynasties
           └── UNCERTAIN     ── Weathered spans flagged for expert paleographer review
```

> **Epigraphic Rule**: The platform never silently invents or hallucinates missing text. Damaged or ambiguous characters are explicitly demarcated using square brackets `[...]` to preserve archaeological authenticity.

---

## Contributing

Contributions from epigraphists, archaeologists, computational linguists, and software engineers are welcome:

1. Fork the repository (`https://github.com/Triguneswar/EPIGRAPH-AI/fork`).
2. Create your feature branch (`git checkout -b feat/new-script-support`).
3. Commit your changes (`git commit -m "feat: add support for Brahmi variant"`).
4. Push to the branch (`git push origin feat/new-script-support`).
5. Open a Pull Request.

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Developed for the preservation, digital archival, and universal decipherment of world epigraphic heritage.</sub>
</div>
