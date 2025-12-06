# ViralLab - AI-Powered YouTube Content Creation Platform

<p align="center">
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react" alt="React 19" />
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker" alt="Docker" />
</p>

ViralLab is a full-stack AI-powered platform that helps YouTube creators generate viral content. From scripts to thumbnails to voiceovers - all powered by GPT-4 and Google Gemini.

---

## ✨ Features

### 🎬 Content Generation

| Feature               | Description                                                                    |
| --------------------- | ------------------------------------------------------------------------------ |
| **Script Generation** | AI analyzes viral YouTube videos and generates optimized scripts for any topic |
| **Thumbnail Studio**  | Generate eye-catching thumbnails with AI (Google Gemini)                       |
| **Face Integration**  | Upload your face and have it seamlessly integrated into thumbnails             |
| **Neural Audio**      | Professional text-to-speech voiceovers with multiple voices and personas       |
| **Image Generation**  | Generate any image from a text prompt with optional face integration           |

### 🔄 Workflow Features

| Feature                   | Description                                              |
| ------------------------- | -------------------------------------------------------- |
| **One-Click Workflow**    | Generate script + thumbnails + audio in a single request |
| **Real-time Streaming**   | Server-Sent Events (SSE) for live progress updates       |
| **Background Processing** | Generate content while you work on other things          |
| **Multi-model Support**   | GPT-4, GPT-3.5, Gemini Pro, and more                     |

### 🔐 Security & Storage

| Feature                   | Description                                           |
| ------------------------- | ----------------------------------------------------- |
| **JWT Authentication**    | Secure user authentication with access/refresh tokens |
| **Session Management**    | Multi-device login with session tracking              |
| **CloudFlare R2 Storage** | Optional cloud storage for generated media            |
| **Local Storage Mode**    | Works offline with local file storage                 |

---

## 🛠️ Tech Stack

### Backend

| Technology         | Purpose                                       |
| ------------------ | --------------------------------------------- |
| **FastAPI**        | High-performance async Python web framework   |
| **PostgreSQL**     | Primary database with async support (asyncpg) |
| **SQLAlchemy 2.0** | Async ORM for database operations             |
| **Alembic**        | Database migrations                           |
| **LangChain**      | AI/LLM orchestration framework                |
| **OpenAI GPT-4**   | Script generation and text processing         |
| **Google Gemini**  | Image/thumbnail generation                    |
| **Pydantic**       | Data validation and settings management       |
| **python-jose**    | JWT token handling                            |
| **bcrypt**         | Password hashing                              |
| **boto3**          | CloudFlare R2 / S3 storage client             |

### Frontend

| Technology         | Purpose                               |
| ------------------ | ------------------------------------- |
| **React 19**       | Modern React with concurrent features |
| **TypeScript**     | Type-safe JavaScript                  |
| **Vite 7**         | Fast build tool and dev server        |
| **Tailwind CSS 4** | Utility-first styling                 |
| **Framer Motion**  | Smooth animations                     |
| **React Router 7** | Client-side routing                   |
| **Lucide React**   | Beautiful icon library                |

### Infrastructure

| Technology         | Purpose                       |
| ------------------ | ----------------------------- |
| **Docker**         | Containerization              |
| **Docker Compose** | Multi-container orchestration |
| **CloudFlare R2**  | S3-compatible object storage  |
| **PostgreSQL 16**  | Production database           |

---

## 📁 Project Structure

```
youtuber/
├── backend/                    # FastAPI Backend
│   ├── alembic/               # Database migrations
│   ├── core/                  # Core configuration
│   │   ├── config.py          # App settings & env vars
│   │   ├── database.py        # Async database setup
│   │   ├── dependencies.py    # FastAPI dependencies
│   │   └── security.py        # JWT & password utils
│   ├── models/                # Data models
│   │   ├── db_models.py       # SQLAlchemy models
│   │   └── schemas.py         # Pydantic schemas
│   ├── routers/               # API endpoints
│   │   ├── auth.py            # Authentication routes
│   │   ├── audio.py           # Audio generation
│   │   ├── face.py            # Face upload/management
│   │   ├── image.py           # Image generation
│   │   ├── script.py          # Script generation
│   │   ├── thumbnail.py       # Thumbnail generation
│   │   ├── workflow.py        # Full workflow orchestration
│   │   └── ...
│   ├── services/              # Business logic
│   │   ├── auth_service.py    # Authentication logic
│   │   ├── storage_service.py # R2/local storage
│   │   ├── workflow_service.py # Workflow orchestration
│   │   └── ...
│   ├── tests/                 # Backend tests
│   └── main.py               # FastAPI app entry point
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── api/              # API client functions
│   │   ├── components/       # React components
│   │   │   ├── ui/           # Reusable UI components
│   │   │   └── CrystalDock.tsx # Navigation dock
│   │   ├── context/          # React contexts
│   │   │   └── AuthContext.tsx # Authentication state
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Route pages
│   │   │   ├── WorkflowPage.tsx
│   │   │   ├── ThumbnailStudioPage.tsx
│   │   │   ├── ImageStudioPage.tsx
│   │   │   ├── AudioStudioPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   └── ...
│   │   ├── types/            # TypeScript types
│   │   ├── App.tsx           # Landing page
│   │   └── Dashboard.tsx     # Main dashboard
│   ├── package.json
│   └── vite.config.ts
│
├── src/                       # Core Python Services
│   ├── script_generator.py    # AI script generation
│   ├── thumbnail_generator.py # Gemini thumbnail generation
│   ├── thumbnail_analyzer.py  # Reference image analysis
│   ├── audio_genreator.py     # OpenAI TTS audio
│   ├── video_fetcher.py       # YouTube video fetching
│   └── transcript_scraper.py  # Video transcript extraction
│
├── docker-compose.yml         # Docker orchestration
├── Dockerfile                 # Production image
├── Dockerfile.dev             # Development image
└── requirements.txt           # Python dependencies
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **PostgreSQL 16+** (or Docker)
- **API Keys:**
  - OpenAI API Key (for scripts & audio)
  - Google Gemini API Key (for thumbnails & images)

### Quick Start with Docker

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/youtuber.git
cd youtuber

# 2. Copy environment file and add your API keys
cp .env.example .env
# Edit .env with your API keys

# 3. Start with Docker Compose
docker compose up --build

# App will be available at http://localhost:8001
```

### Local Development

```bash
# Backend Setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Start PostgreSQL (or use Docker)
docker compose up db -d

# Run migrations
cd backend && alembic upgrade head

# Start backend
uvicorn backend.main:app --reload --port 8001

# Frontend Setup (new terminal)
cd frontend
npm install
npm run dev

# Frontend at http://localhost:5173
# Backend at http://localhost:8001
```

---

## 🔑 Environment Variables

```env
# API Keys (Required)
OPENAI_API_KEY=sk-your-openai-key
GEMINI_API_KEY=your-gemini-key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/youtuber

# JWT Security
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# Optional: CloudFlare R2 Storage
STORAGE_MODE=local  # or "r2"
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=virallab-media
R2_PUBLIC_URL=
```

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint         | Description           |
| ------ | ---------------- | --------------------- |
| POST   | `/auth/signup`   | Register new user     |
| POST   | `/auth/login`    | Login and get tokens  |
| POST   | `/auth/refresh`  | Refresh access token  |
| POST   | `/auth/logout`   | Logout current device |
| GET    | `/auth/me`       | Get current user info |
| GET    | `/auth/sessions` | List active sessions  |

### Content Generation

| Method | Endpoint                         | Description                     |
| ------ | -------------------------------- | ------------------------------- |
| POST   | `/generate/script`               | Generate YouTube script         |
| POST   | `/generate/thumbnail`            | Generate thumbnails             |
| POST   | `/generate/full-workflow`        | Script + thumbnails in one call |
| POST   | `/generate/full-workflow/stream` | Streaming workflow with SSE     |

### Audio

| Method | Endpoint          | Description                     |
| ------ | ----------------- | ------------------------------- |
| GET    | `/audio/options`  | Get available voices & personas |
| POST   | `/audio/generate` | Generate voiceover audio        |
| GET    | `/audio/list`     | List user's audio files         |

### Images

| Method | Endpoint          | Description                  |
| ------ | ----------------- | ---------------------------- |
| POST   | `/image/generate` | Generate images from prompt  |
| GET    | `/image/list`     | List user's generated images |

### Face Management

| Method | Endpoint        | Description            |
| ------ | --------------- | ---------------------- |
| POST   | `/face/upload`  | Upload face image      |
| GET    | `/face/current` | Get current face image |
| DELETE | `/face/current` | Delete face image      |

---

## 🎨 Frontend Pages

| Page                 | Path                   | Description            |
| -------------------- | ---------------------- | ---------------------- |
| **Landing**          | `/`                    | Marketing landing page |
| **Login**            | `/login`               | User authentication    |
| **Signup**           | `/signup`              | New user registration  |
| **Dashboard**        | `/dashboard`           | Main app dashboard     |
| **Workflow**         | `/dashboard/workflow`  | Full content workflow  |
| **Thumbnail Studio** | `/dashboard/thumbnail` | Generate thumbnails    |
| **Image Studio**     | `/dashboard/image`     | Generate images        |
| **Audio Studio**     | `/dashboard/audio`     | Generate voiceovers    |
| **Settings**         | `/dashboard/settings`  | User settings          |

---

## 🐳 Docker Commands

```bash
# Production build & run
docker compose up --build

# Development mode (with hot reload)
docker compose --profile dev up db frontend-dev backend-dev

# Just the database
docker compose up db

# View logs
docker compose logs -f app

# Stop all services
docker compose down

# Clean volumes
docker compose down -v
```

---

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_auth.py -v
```

---

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/yourusername">Aditya Pratap Singh</a>
</p>
