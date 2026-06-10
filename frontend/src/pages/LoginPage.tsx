import React from "react";
import { LoginForm } from "../components/auth/LoginForm";

interface LoginPageProps {
  onSuccess: () => void;
  onToggleRegister: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSuccess, onToggleRegister }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <LoginForm onSuccess={onSuccess} onToggleRegister={onToggleRegister} />
    </div>
  );
};
