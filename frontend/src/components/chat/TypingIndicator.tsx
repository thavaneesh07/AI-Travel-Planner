import React from "react";

export const TypingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex items-center space-x-2 bg-gray-100 border border-gray-200 p-4 rounded-3xl rounded-tl-none max-w-[80%] text-sm">
        <span className="text-base">🤖</span>
        <span className="text-gray-500 font-medium animate-pulse">Typing...</span>
      </div>
    </div>
  );
};
