import React, { useState } from "react";
import { PlannerPage } from "./pages/PlannerPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { SavedTripsPage } from "./pages/SavedTripsPage";
import { ErrorBoundary } from "./components/shared/ErrorBoundary";

function App() {
  const [currentView, setCurrentView] = useState("planner");

  const renderView = () => {
    switch (currentView) {
      case "planner":
        return (
          <PlannerPage
            onNavigateToSaved={() => setCurrentView("saved-trips")}
            onNavigateToLogin={() => setCurrentView("login")}
          />
        );
      case "login":
        return (
          <LoginPage
            onSuccess={() => setCurrentView("planner")}
            onToggleRegister={() => setCurrentView("register")}
          />
        );
      case "register":
        return (
          <RegisterPage
            onSuccess={() => setCurrentView("planner")}
            onToggleLogin={() => setCurrentView("login")}
          />
        );
      case "saved-trips":
        return (
          <SavedTripsPage
            onBackToPlanner={() => setCurrentView("planner")}
          />
        );
      default:
        return (
          <PlannerPage
            onNavigateToSaved={() => setCurrentView("saved-trips")}
            onNavigateToLogin={() => setCurrentView("login")}
          />
        );
    }
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">{renderView()}</div>
    </ErrorBoundary>
  );
}

export default App;
