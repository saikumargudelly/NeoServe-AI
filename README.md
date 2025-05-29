# NeoServe AI

A multi-agent system for customer service and engagement built with FastAPI and Google Cloud Platform.

## Features

- **Multi-Agent Architecture**: Modular design with specialized agents for different tasks
- **Intent Classification**: Understands user intents using machine learning
- **Knowledge Base**: Answers FAQs using a comprehensive knowledge base
- **Personalization**: Tailors responses based on user profiles and history
- **Proactive Engagement**: Sends timely messages and follow-ups
- **Human Handoff**: Seamlessly escalates to human agents when needed
- **RESTful API**: Fully documented API for easy integration

## Getting Started

### Prerequisites

- Python 3.8+
- Google Cloud Platform account
- Docker (for containerized deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/neoserve-ai.git
   cd neoserve-ai
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .[dev]  # For development
   # or
   pip install -e .  # For production
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Configuration

Create a `.env` file in the project root with the following variables:

```env
# General
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_RELOAD=True

# Authentication
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
ALGORITHM=HS256
```

## Running the Application

### Development

```bash
uvicorn neoserve_ai.main:app --reload
```

The API will be available at `http://localhost:8000`

### Production

For production, use a production-grade ASGI server like Uvicorn with Gunicorn:

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 neoserve_ai.main:app
```

### Docker

Build the Docker image:

```bash
docker build -t neoserve-ai .
```

Run the container:

```bash
docker run -d --name neoserve-ai -p 8000:8000 --env-file .env neoserve-ai
```

## API Documentation

Once the application is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Testing

Run tests with pytest:

```bash
pytest tests/
```

With coverage:

```bash
pytest --cov=neoserve_ai tests/
```

## Project Structure

```
neoserve_ai/
├── api/                    # API routes and endpoints
│   └── api_v1/             # API version 1
│       ├── endpoints/       # API endpoint modules
│       └── api.py          # API router configuration
├── agents/                 # Agent implementations
│   ├── base_agent.py       # Base agent class
│   ├── intent_classifier.py # Intent classification agent
│   ├── knowledge_agent.py  # Knowledge base agent
│   ├── personalization_agent.py # Personalization agent
│   ├── proactive_engagement_agent.py # Proactive engagement agent
│   ├── escalation_agent.py # Escalation agent
│   └── orchestrator.py     # Agent orchestrator
├── config/                 # Configuration
│   └── settings.py         # Application settings
├── models/                 # Database models
├── schemas/                # Pydantic models
├── services/               # Business logic
├── utils/                  # Utility functions
│   └── auth.py             # Authentication utilities
├── main.py                 # Application entry point
└── requirements.txt        # Production dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FastAPI for the awesome web framework
- Google Cloud Platform for the AI and infrastructure services
- All contributors who have helped improve this project
