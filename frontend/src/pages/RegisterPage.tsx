import React from "react";
import { RegisterForm } from "../components/auth/RegisterForm";

interface RegisterPageProps {
  onSuccess: () => void;
  onToggleLogin: () => void;
}

export const RegisterPage: React.FC<RegisterPageProps> = ({ onSuccess, onToggleLogin }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <RegisterForm onSuccess={onSuccess} onToggleLogin={onToggleLogin} />
    </div>
  );
};
