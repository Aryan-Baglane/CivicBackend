# Civic Backend - AI-Powered Civic Issue Automation

An intelligent backend system for automating civic issue reporting through multiple channels (Email, Voice, Web). Built with FastAPI, powered by Gemini LLM and Crawl4AI web scraping.

## 🚀 Features

- **Multi-Channel Automation**: Email drafting, Voice agent scripts, and Web reporting
- **Smart Authority Discovery**: AI-powered classification and contact information extraction
- **Advanced Web Scraping**: Crawl4AI-powered scraping with category-specific logic
- **Image Attachments**: Support for attaching evidence photos to complaints
- **Voice Agent Simulation**: Generates natural call scripts for in-app TTS

## 📋 API Endpoints

### 1. Main Automation Endpoint
**POST** `/automation/start`

Execute civic actions (Email, Call, Web).

**Request:**
```json
{
  "issue": {
    "description": "Pothole causing traffic",
    "location": "Bangalore",
    "category": "Road",
    "images": ["file:///..."]
  },
  "channel": "EMAIL"
}
```

**Response (EMAIL):**
```json
{
  "action": "OPEN_EMAIL",
  "payload": {
    "to": "official@authority.gov.in",
    "subject": "Formal Complaint...",
    "body": "...",
    "attachments": ["file:///..."]
  }
}
```

**Response (CALL):**
```json
{
  "action": "START_VOICE_AGENT",
  "payload": {
    "script": "Hello, I am calling on behalf...",
    "authority_name": "Municipal Corporation",
    "location": "Bangalore"
  }
}
```

### 2. Issue Analysis
**POST** `/issue/`

Analyze and classify civic issues.

```json
{
  "description": "Broken streetlight",
  "location": "Delhi"
}
```

### 3. Chat Assistant
**POST** `/chat/`

General civic assistance chatbot.

## 🛠️ Local Development

### Prerequisites
- Python 3.11+
- Git

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Aryan-Baglane/CivicBackend.git
cd CivicBackend
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install chromium
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

4. **Run the server:**
```bash
cd backend
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`

## 🌐 Deployment (Render)

### Automatic Deployment

1. **Fork/Push this repository to GitHub**

2. **Connect to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

3. **Set Environment Variables:**
   - Add `OPENROUTER_API_KEY` in Render dashboard
   - Other vars are configured in `render.yaml`

4. **Deploy:**
   - Render automatically builds and deploys
   - Access your API at `https://your-service.onrender.com`

### Manual Deployment

If using Render's manual setup:
- **Build Command:** `pip install -r requirements.txt && playwright install chromium`
- **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment:** Python 3.11

## 📁 Project Structure

```
CivicBackend/
├── backend/
│   ├── agents/          # AI agents (email, call, scraper)
│   ├── api/             # FastAPI endpoints
│   ├── services/        # Business logic
│   ├── database.py      # SQLite persistence
│   └── main.py          # App entry point
├── requirements.txt     # Python dependencies
├── render.yaml          # Render deployment config
└── .env.example         # Environment template
```

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | OpenRouter API key (for LLM calls) | Yes |
| `OPENROUTER_MODEL` | Model to use (default: `google/gemini-2.0-flash-001`) | No |
| `OPENROUTER_BASE_URL` | OpenRouter base URL (default: `https://openrouter.ai/api/v1`) | No |

## 🧪 Testing

Test the automation endpoint:
```bash
curl -X POST "http://localhost:8000/automation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "issue": {
      "description": "Pothole",
      "location": "Bangalore"
    },
    "channel": "EMAIL"
  }'
```

## 📚 Tech Stack

- **FastAPI**: Modern Python web framework
- **Crawl4AI**: Advanced web scraping
- **Google Gemini**: LLM for classification and content generation
- **Playwright**: Browser automation
- **SQLite**: Lightweight database

## 🤝 Contributing

Pull requests welcome! Please ensure:
- Code follows existing patterns
- All endpoints are tested
- Environment variables are documented

## 📄 License

MIT License

## 👤 Author

Aryan Baglane
