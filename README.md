# Bookmark Shortener API 🔗

A high-performance, asynchronous REST API for shortening URLs, managing user bookmarks, and tracking click analytics. Built with **FastAPI**, **SQLAlchemy (Async)**, **PostgreSQL**, and **uv**.

---

## ✨ Features

- **User Authentication**: Secure user registration and JWT-based Bearer token authentication.
- **URL Shortener**: Generate unique short codes for long URLs.
- **Analytics & Tracking**: Non-blocking background analytics tracking visit counts and timestamps per bookmark.
- **Pagination & Search**: List bookmarks with `skip` & `limit` pagination and case-insensitive keyword `search`.
- **Rate Limiting**: Custom sliding-window rate limiting middleware to prevent API abuse.
- **Async Database Stack**: Powered by SQLAlchemy 2.0 Async engine with PostgreSQL (`asyncpg`) and Alembic migrations.

---

## 🚀 Quick Start

### Prerequisites
- [Python 3.14+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) package manager
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rejul-newformtech/bookmark-shortner.git
   cd bookmark-shortner
   ```

2. **Install dependencies**:
   ```bash
   uv sync --dev
   ```

3. **Set environment variables**:
   Create a `.env` file in the root directory:
   ```env
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=bookmark_db
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   LOG_FORMAT=text
   LOG_DIR=logs
   ```

4. **Run Database Migrations**:
   ```bash
   uv run alembic upgrade head
   ```

5. **Start Development Server**:
   ```bash
   make dev
   ```
   The API will be available at `http://localhost:8000`. Interactive API documentation (Swagger UI) is available at `http://localhost:8000/docs`.

---

## 🐳 Running with Docker

Start PostgreSQL and the FastAPI application in containerized mode:

```bash
make docker-up
```

Stop containers:
```bash
make docker-down
```

---

## 📌 API Endpoints

### Authentication (`/auth`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Authenticate and obtain JWT token |

### User Profile (`/users`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/users/profile` | Get current authenticated user profile |

### Bookmarks (`/bookmarks`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/bookmarks/` | Create a short URL bookmark |
| `GET` | `/bookmarks/?skip=0&limit=10&search=keyword` | List user bookmarks with pagination & search |
| `GET` | `/bookmarks/{short_code}` | Resolve short URL and trigger background visit analytics |

---

## 🧪 Testing & Code Quality

Run tests, typechecking, and linting with Make commands:

```bash
# Run pytest suite
make test

# Format code with Ruff
make format

# Lint code with Ruff
make lint

# Typecheck with MyPy
make typecheck
```
