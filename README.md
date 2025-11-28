# 🎓 Agentic AI for Curriculum-Aligned Educational Video Generation

A web application that enables educators to **generate curriculum-aligned educational videos** from simple text prompts or uploaded study materials.  
Built using **Next.js**, **FastAPI**, **Supabase**, and an **Agentic AI orchestration pipeline** powered by open-source LLMs and **Manim** for animation rendering.

---

## 🚀 Overview

The platform automates the creation of **animated educational videos** using Agentic AI — where multiple specialized AI agents (Planner, Script, CodeGen, Reviewer) work together to generate scripts, animation code, and rendered videos.

Educators can log in, provide a topic prompt or upload documents, and receive an **auto-generated video** aligned with their course material.

---

## 🧩 Tech Stack

### Frontend
- **Next.js** — React-based framework for the web app interface  
- **Tailwind CSS** — for styling and responsive design  
- **Supabase Auth** — for user authentication and session management  
- **Video.js / React Player** — for video playback  

### Backend
- **FastAPI** — REST API service handling orchestration and job management  
- **Python 3.10+**  
- **Manim** — for animation generation  
- **FFmpeg** — for video post-processing and stitching  
- **Docker** — for containerized backend deployment  

### AI Layer
- **Open-source LLMs** (LLaMA, Mistral, DeepSeek) via local inference  
- **LangChain / AutoGen** — for agent orchestration  
- **RAG (Retrieval-Augmented Generation)** — for extracting relevant curriculum content  
- **Sentence Transformers / Chroma DB** — for embeddings and semantic search  

### Database & Storage
- **PostgreSQL (Supabase)** — for structured data  
- **Supabase Storage / S3** — for video file storage  

### Deployment
- **Frontend:** Vercel  
- **Backend:** Docker container (Render / local server)  

---

## 🧠 Agentic AI Architecture

The **Agentic AI Orchestrator** coordinates multiple agents:

1. **Planner Agent** – Breaks the topic into structured learning segments.  
2. **Script Agent** – Generates clear explanations and narration.  
3. **CodeGen Agent** – Converts descriptions into Manim Python code.  
4. **Reviewer Agent** – Validates and corrects code before rendering.  
5. **Tool Adapter** – Handles LLM calls, RAG context retrieval, and rendering tasks.

Agents communicate using structured **JSON artifacts** for reliable processing.

---

## ⚙️ Project Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-org>/<repo-name>.git
cd <repo-name>
```

---

## 📁 Folder Structure

```
/project-root
│
├── frontend/          # Next.js + Tailwind + Supabase
├── backend/           # FastAPI + Agentic AI pipeline + Manim
├── docs/              # Architecture diagrams, SRS, reports
└── README.md
```

---

## 🖥️ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Create `.env.local`:

```
NEXT_PUBLIC_SUPABASE_URL=<your_supabase_url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your_supabase_anon_key>
```

---

## 🖧 Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

`.env`:

```
SUPABASE_URL=<supabase_url>
SUPABASE_SERVICE_KEY=<service_key>
DATABASE_URL=<postgres_url>
```

---

## 🐳 Running Backend with Docker

```bash
docker build -t manim-backend .
docker run -p 8000:8000 manim-backend
```

---

## 🧱 Development Standards

### 1. Branching Strategy

- `main` → stable
- `dev` → active development
- `feature/<name>` → for new features
- `fix/<issue>` → bug fixes

### 2. Commit Message Convention

| Type | Example |
|------|---------|
| `feat:` | feat: add login UI |
| `fix:` | fix: incorrect API path |
| `docs:` | docs: update README |
| `chore:` | chore: remove unused files |

---

## 👨‍💻 Coding Conventions

### Frontend
- Use **TypeScript** and React hooks  
- Tailwind CSS for styling  
- Run ESLint before committing  

### Backend
- Follow **PEP8**  
- Use `black` + `flake8`  
- Add docstrings for all endpoints  

---

## 📦 AI & RAG Integration

### RAG Pipeline
- Uses Supabase Vector or Chroma DB  
- Embeddings with `all-MiniLM-L6-v2`  
- Retrieves top-k chunks for grounding  

### Manim Rendering Flow
- CodeGen agent creates Manim scripts  
- Docker sandbox executes them safely  
- FFmpeg merges scenes + audio  

---

## 📈 Long-Term Roadmap

| Phase | Goal | Timeline |
|-------|------|----------|
| Phase 1 | Basic text → video pipeline | Oct–Dec 2024 |
| Phase 2 | Add voiceovers, polished UX | Jan 2025 |
| Phase 3 | Mobile app + interactive learning | Feb–Mar 2025 |

---

## 🧾 License

This project is open-source under the **MIT License**.

---

## 👥 Team

- **Mayank Salunkhe | Mustansir Rangwala** — Frontend & Supabase  
- **Samruddhi Kadam | Mustansir Rangwala** — Backend & AI Pipeline
- **Sanika Shinde | Mustansir Rangwala** — Agent Design

---

## 💬 Support

If you face any setup issues, please open an issue in the repository.

