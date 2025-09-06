# CryptoSentinel Deployment Guide

This guide provides instructions on how to set up and run the CryptoSentinel application, which consists of a Python backend and a React frontend.

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Git

## 1. Backend Setup

The backend is a FastAPI application that serves the API and runs the AI agent team.

### a. Clone the Repository

```bash
git clone <repository_url>
cd <repository_directory>
```

### b. Install Python Dependencies

Navigate to the `backend` directory and install the required packages:

```bash
cd backend
pip install -r requirements.txt
```

### c. Configure Environment Variables

The backend requires a `.env` file inside the `backend` directory with the following variables:

```
# backend/.env

# The Gemini model to use for the agents
gemini_model="gemini-1.5-flash-latest"

# The temperature for the model's responses
temperature=0.7

# A comma-separated list of your Google AI API keys for Gemini
gemini_api_keys="YOUR_API_KEY_1,YOUR_API_KEY_2,..."
```

Replace `YOUR_API_KEY_1,...` with your actual Google AI API keys. The system will rotate through these keys if it encounters resource exhaustion errors.

### d. Run the Backend Server

From the **root** of the project directory, run the following command:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The backend server will now be running on `http://localhost:8000`.

## 2. Frontend Setup

The frontend is a React application built with Vite.

### a. Install Node.js Dependencies

From the **root** of the project directory, run:

```bash
npm install
```

### b. Run the Frontend Development Server

To run the frontend in development mode (with hot-reloading):

```bash
npm run dev
```

The frontend will be available at `http://localhost:8080` (as configured in `vite.config.ts`).

### c. Building for Production

To create a production build of the frontend:

```bash
npm run build
```

This will create a `dist` directory containing the static assets. You can serve the contents of this directory with a static file server like `serve`:

```bash
npm install -g serve
serve -s dist
```

## 3. Application Usage

1.  Start both the backend and frontend servers as described above.
2.  Open your web browser and navigate to the frontend URL (e.g., `http://localhost:8080`).
3.  In the application's "Settings" tab, ensure the "API URL" is set to your backend's address (`http://localhost:8000`).
4.  In the application's "Settings" tab, you must provide a value for the API key. The backend requires an `Authorization` header for all requests, but it uses the `gemini_api_keys` from the `.env` file for all AI agent operations. You can enter any non-empty string (e.g., "placeholder") in the API key field in the frontend settings to proceed.
5.  The application should now be fully functional.
