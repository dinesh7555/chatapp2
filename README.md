# Chat App

A full-stack AI-powered chat application with user authentication, real-time conversations, and intelligent memory management using graph databases.

## Features

- **User Authentication**: Secure registration and login with JWT tokens
- **AI-Powered Chat**: Conversations with Llama 3 model via OpenRouter API
- **Intelligent Memory**: Topic-based context retrieval using Neo4j graph database
- **Modern UI**: Responsive React frontend with real-time chat interface
- **Scalable Architecture**: Microservices setup with Docker containers

## Tech Stack

### Backend

- **FastAPI**: High-performance web framework
- **SQLAlchemy**: ORM for MySQL database
- **Neo4j**: Graph database for chat memory and relationships
- **Pydantic**: Data validation and serialization
- **JWT**: Authentication tokens

### Frontend

- **React**: UI library with hooks
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API calls
- **React Router**: Client-side routing
- **React Markdown**: Message rendering

### Infrastructure

- **Docker & Docker Compose**: Containerization and orchestration
- **MySQL**: Relational database for user data
- **Neo4j**: Graph database for chat relationships

## Project Structure

```
chat-app/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── auth.py
│       ├── chat.py
│       ├── config.py
│       ├── database.py
│       ├── llm.py
│       ├── main.py
│       ├── models.py
│       ├── neo4j_db.py
│       ├── schemas.py
│       ├── __pycache__/
│       ├── repositories/
│       │   ├── conversation_repo.py
│       │   ├── memory_repo.py
│       │   ├── message_repo.py
│       │   └── topic_repo.py
│       └── services/
│           ├── llm_service.py
│           ├── semantic_memory.py
│           └── title_service.py
├── frontend/
│   ├── Dockerfile
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── README.md
│   ├── vite.config.js
│   ├── public/
│   └── src/
│       ├── App.css
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       ├── router.jsx
│       ├── api/
│       │   ├── auth.js
│       │   ├── chat.js
│       │   └── http.js
│       ├── assets/
│       ├── components/
│       │   ├── chat/
│       │   │   ├── chat.css
│       │   │   ├── ChatInput.jsx
│       │   │   ├── ChatMessage.jsx
│       │   │   └── ChatWindow.jsx
│       │   └── layout/
│       │       ├── layout.css
│       │       ├── Layout.jsx
│       │       ├── Sidebar.jsx
│       │       └── Topbar.jsx
│       └── pages/
│           ├── auth.css
│           ├── Login.jsx
│           └── Register.jsx


## Prerequisites

- Docker and Docker Compose
- OpenRouter API key (for AI chat functionality)

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd chat-app
   ```

2. **Set up environment variables**

   Create a `.env` file in the `backend/` directory:

   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

3. **Start the application**

   ```bash
   docker-compose up --build
   ```

   This will start all services:

   - MySQL database (port 3306)
   - Neo4j database (ports 7474, 7687)
   - Backend API (port 8000)
   - Frontend (port 5173)

## Usage

1. **Access the application**

   - Open your browser and go to `http://localhost:5173`

2. **Register a new account**

   - Click "Register" and create your account

3. **Start chatting**
   - Login with your credentials
   - Begin conversations with the AI assistant
   - The system maintains context through intelligent topic-based memory

## API Endpoints

### Authentication

- `POST /register` - User registration
- `POST /login` - User login
- `GET /protected` - Protected route (requires authentication)

### Chat

- `POST /chat/send` - Send a message
- `GET /chat/history` - Get chat history
- `GET /chat/topics` - Get conversation topics

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Database Setup

The application uses two databases:

- **MySQL**: Stores user accounts and basic data
- **Neo4j**: Manages chat relationships, topics, and memory

Database schemas are automatically created on startup.

## Configuration

Key configuration options in `backend/.env`:

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `DATABASE_URL`: MySQL connection string
- `NEO4J_URI`: Neo4j connection URI

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
