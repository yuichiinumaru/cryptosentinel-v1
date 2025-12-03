# CryptoSentinel - Autonomous Cryptocurrency Trading Bot

## 1. Project Overview

CryptoSentinel is an advanced, autonomous trading bot for cryptocurrencies. It is designed to provide secure, efficient, and intelligent trading capabilities. The system utilizes a multi-agent AI framework to analyze market data, execute trades, and continuously learn and improve its strategies.

This project is a full-stack application with a Python backend and a React/TypeScript frontend. The backend is a sophisticated multi-agent system built with FastAPI and the Agency Swarm framework. The frontend is a comprehensive dashboard for monitoring and interacting with the backend.

## 2. Features

*   **Real-time Dashboard:** A comprehensive overview of trading activity, funds, agent activities, and market data.
*   **Autonomous Trading:** The system executes trades automatically based on market analysis and configured strategies.
*   **Multi-Agent AI System:** A team of specialized AI agents for market analysis, trading, risk management, and more.
*   **Advanced Security:** Features like MEV protection, rug pull detection, and fund isolation to ensure the security of your assets.
*   **Technical and Fundamental Analysis:** In-depth analysis of market data, news, and social sentiment.
*   **AI Learning System:** The system continuously learns and improves its strategies based on historical data.
*   **Customization:** The ability to customize the system's configuration, including API keys and trading strategies.

## 3. Architecture

The system is composed of two main components: a backend and a frontend.

### 3.1. Backend

The backend is a Python application built with FastAPI and the Agency Swarm framework. It is a multi-agent system with 12 specialized AI agents that collaborate to perform trading tasks. The agents communicate with each other using a standardized messaging protocol and use a variety of tools to interact with the outside world.

For more details on the backend architecture and the individual agents, please refer to the documentation in the `docs` directory.

### 3.2. Frontend

The frontend is a React/TypeScript application that provides a user-friendly interface for interacting with the backend. It uses the TanStack Query library for data fetching and state management, and the `shadcn/ui` component library for the UI. The frontend communicates with the backend through a REST API.

## 4. Getting Started

To get started with CryptoSentinel, you will need to set up both the backend and the frontend.

### 4.1. Backend Setup

1.  Navigate to the `backend` directory: `cd backend`
2.  Install the required dependencies: `pip install -r requirements.txt`
3.  Create a `.env` file and configure your API keys and other settings.
4.  Run the backend server: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

### 4.2. Frontend Setup

1.  Navigate to the root directory of the project.
2.  Install the required dependencies: `npm install`
3.  Run the frontend development server: `npm run dev`

## 5. Usage

Once the backend and frontend are running, you can access the application in your web browser at `http://localhost:5173`. From the dashboard, you can monitor the system's activity, view market data, and interact with the AI agents.

## 6. Testing

The project includes a suite of tests for both the backend and the frontend.

### 6.1. Backend Tests

To run the backend tests, navigate to the `backend` directory and run the following command:

```bash
pytest
```

### 6.2. Frontend Tests

To run the frontend tests, navigate to the root directory of the project and run the following command:

```bash
npm test
```

## 7. Documentation

This `README.md` file provides a high-level overview of the project. For more detailed documentation, please refer to the files in the `docs` directory. The `docs` directory contains the following documents:

*   `TDD.md`: A guide to the Test-Driven Development (TDD) methodology and its application to this project.
*   `old/`: A directory containing the old documentation files.

## 8. Contributing

We welcome contributions to CryptoSentinel! If you would like to contribute, please follow these.

## 9. License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
