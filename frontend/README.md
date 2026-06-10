# AI Travel Planner - Frontend

This is the frontend application for the **AI Travel Planner**, a smart travel assistant that generates personalized travel itineraries, parses natural language queries, and provides hotel suggestions and weather forecasts.

## 🚀 Features

- **Interactive Maps:** View your travel destinations and itineraries on interactive maps powered by `Leaflet` and `React-Leaflet`.
- **Dynamic Animations:** Smooth transitions and beautiful micro-animations using `Framer Motion`.
- **Modern UI/UX:** Fully responsive and premium design styled with `Tailwind CSS`.
- **Data Visualization:** Charts and visual representations of travel data using `Recharts`.
- **State Management:** Efficient client-side state management with `Zustand`.
- **AI-Powered:** Connects to the FastAPI backend to parse natural language queries and generate detailed travel plans.

## 🛠️ Tech Stack

- **Framework:** React 19 + Vite
- **Styling:** Tailwind CSS + PostCSS
- **Animations:** Framer Motion
- **Maps:** Leaflet & React-Leaflet
- **Charts:** Recharts
- **State Management:** Zustand
- **HTTP Client:** Axios

## 📦 Getting Started

### Prerequisites

- Node.js (v18 or higher recommended)
- npm or yarn

### Installation

1. Navigate to the frontend directory (if not already there):
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Running the Development Server

Start the Vite development server:
```bash
npm run dev
```
The application will be available at `http://localhost:5173`.

### Building for Production

To create a production build:
```bash
npm run build
```

To preview the production build locally:
```bash
npm run preview
```

## 🔗 Backend Integration

This frontend is designed to work with the AI Travel Planner FastAPI backend. Ensure the backend server is running (typically on `http://127.0.0.1:8000`) so that API calls (e.g., `/api/plan`, `/api/parse`, `/chat`) function correctly.
