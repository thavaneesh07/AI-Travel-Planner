import React from "react";

interface RetryButtonProps {
  onRetry: () => void;
  label?: string;
}

export const RetryButton: React.FC<RetryButtonProps> = ({ onRetry, label = "Retry Operation" }) => {
  return (
    <button
      onClick={onRetry}
      className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-xl shadow-md transition-all duration-300 transform hover:scale-102"
    >
      🔄 {label}
    </button>
  );
};
