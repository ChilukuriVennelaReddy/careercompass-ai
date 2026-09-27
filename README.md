# CareerCompass AI

CareerCompass AI is an AI-powered career counselor application tailored for university students and fresh graduates. It provides personalized job recommendations, identifies skill gaps, creates learning roadmaps, and helps with interview preparation.

## Setup

1. **Clone the repository** (if applicable).
2. **Set up a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   Copy the example environment file and add your Anthropic API Key:
   ```bash
   cp .env.example .env
   # Edit .env to add your API key
   ```

## Running Locally

Run the FastAPI server using Uvicorn:
```bash
uvicorn main:app --reload
```
The application will be available at `http://localhost:8000`.

## Docker Deployment

Build the Docker image:
```bash
docker build -t careercompass-ai .
```

Run the Docker container:
```bash
docker run -p 8000:80 --env-file .env careercompass-ai
```
The application will be accessible at `http://localhost:8000`.
