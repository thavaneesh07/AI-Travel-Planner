# AI Travel Planner

**AI Travel Planner** is an intelligent, full-stack application that leverages Artificial Intelligence and Natural Language Processing to generate customized travel itineraries based on user queries. It offers a seamless user experience for discovering destinations, viewing interactive maps, and receiving hotel and weather suggestions.

## ✨ Features

- **Conversational Trip Planning:** Use natural language (e.g., "Plan a 5-day trip to Paris for under $2000 focusing on art and food") to generate comprehensive itineraries.
- **Detailed Itineraries:** Receive daily plans including activities, locations, and schedules.
- **Interactive Maps:** View your destinations on dynamic maps powered by Leaflet.
- **Weather Forecasts:** Check up-to-date weather forecasts for your destination.
- **Hotel Suggestions:** Get tailored hotel recommendations based on your budget and preferences.
- **Modern UI:** A beautiful, responsive interface built with React, Tailwind CSS, and Framer Motion.
- **FastAPI Backend:** A high-performance Python backend powered by FastAPI for processing AI generation and NLP tasks.

## 🏗️ Project Structure

The project is structured into two main applications:

- **/backend:** The FastAPI Python server handling AI models, NLP parsing, external APIs (weather, places), and database interactions.
- **/frontend:** The React + Vite frontend application utilizing Tailwind CSS, Zustand for state management, and Leaflet for maps.

## 🚀 Getting Started

### Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up environment variables (create a `.env` file based on your configuration).
4. Run the FastAPI development server:
   ```bash
   uvicorn app:app --reload
   ```

### Frontend Setup

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install the necessary NPM packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, Pydantic
- **Frontend:** React, Vite, Tailwind CSS, Framer Motion, Zustand, React-Leaflet, Recharts
- **Database:** SQLite / PostgreSQL (configured via SQLAlchemy)

## 📝 License

This project is licensed under the MIT License.
