# 🛠️ Project Setup Guide

This guide will help you set up the project on your local machine. It covers installation for both **Mac** and **Windows**.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

### 1. Git
- **Mac/Windows**: Download from [git-scm.com](https://git-scm.com/downloads)

### 2. Node.js & pnpm
We use **Node.js (LTS)** and **pnpm** for the frontend.
- **Mac**:
  ```bash
  brew install node
  npm install -g pnpm
  ```
- **Windows**:
  - Download Node.js LTS from [nodejs.org](https://nodejs.org/)
  - Open PowerShell as Administrator and run:
    ```powershell
    npm install -g pnpm
    ```

### 3. Python 3.10+
Required for the backend.
- **Mac**: `brew install python`
- **Windows**: Download from [python.org](https://www.python.org/downloads/) (Ensure "Add Python to PATH" is checked).

### 4. Docker Desktop
Required for running the local Supabase instance and database.
- Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
- **Start Docker Desktop** before proceeding.

### 5. Supabase CLI
Required to manage the local database.
- **Mac**:
  ```bash
  brew install supabase/tap/supabase
  ```
- **Windows**:
  - Open PowerShell:
    ```powershell
    npm install -g supabase
    ```
    *(Alternatively, use `scoop install supabase` if you use Scoop)*

---

## 🚀 Setting Up the Project

### 1. Clone the Repository
Open your terminal (Terminal on Mac, PowerShell/Command Prompt on Windows) and run:

```bash
git clone <your-repo-url>
cd <repo-name>
```

### 2. Start Local Supabase
This will spin up the local database and authentication services via Docker.

```bash
supabase start
```
> **Note:** The first time you run this, it may take a while to download Docker images.
>
> 📝 **Important:** Copy the **API URL (`NEXT_PUBLIC_SUPABASE_URL`)** and **anon key (`NEXT_PUBLIC_SUPABASE_ANON_KEY`)** from the output. You will need them for the next steps.

### 3. Frontend Setup

Navigate to the frontend directory:
```bash
cd frontend
```

#### Install Dependencies
```bash
pnpm install
```

#### Configure Environment Variables
Create a `.env.local` file by copying the example (if available) or creating a new one:

**Mac/Linux:**
```bash
cp .env.local.example .env.local
# Or if no example exists:
touch .env.local
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.local.example .env.local
# Or create new:
New-Item .env.local
```

Open `.env.local` in your editor and add the keys you copied from `supabase start`:

```env
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-anon-key-from-supabase-start>
```

#### Run the Frontend
```bash
pnpm dev
```
Open [http://localhost:3000](http://localhost:3000) to view the app.

### 4. Backend Setup

Open a **new terminal** window and navigate to the backend directory:
```bash
cd backend
```

#### Create Virtual Environment

**Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment Variables
Create a `.env` file in the `backend` directory:

```env
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_SERVICE_KEY=<your-service-role-key-from-supabase-start>
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
```
*(Note: Use the `service_role` key for the backend, not the `anon` key. You can find this by running `supabase status` if you lost it).*

#### Run the Backend
```bash
uvicorn main:app --reload
```
The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## 🛠️ Common Commands

| Command | Description |
|---------|-------------|
| `supabase stop` | Stops the local Supabase instance to save resources. |
| `supabase status` | Shows the URLs and Keys for the local instance. |
| `pnpm build` | Builds the frontend for production. |
| `pnpm lint` | Runs linting checks on the frontend. |

## ❓ Troubleshooting

- **Docker not running?** Ensure Docker Desktop is started and the engine is running.
- **Supabase commands fail?** Ensure you are in the root directory where `supabase/config.toml` is located.
- **Port conflicts?** If ports 3000, 8000, or 54321 are in use, stop the conflicting processes.