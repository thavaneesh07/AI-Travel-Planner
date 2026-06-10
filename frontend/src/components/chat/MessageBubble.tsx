import React from "react";

interface MessageBubbleProps {
  role: "user" | "assistant";
  text: string;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ role, text }) => {
  const isUser = role === "user";
  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`flex items-start max-w-[80%] p-4 rounded-3xl shadow-sm text-sm leading-relaxed ${
          isUser
            ? "bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-tr-none"
            : "bg-gray-100 text-gray-800 rounded-tl-none border border-gray-200"
        }`}
      >
        <span className="mr-2 text-base">{isUser ? "👤" : "🤖"}</span>
        <span className="whitespace-pre-wrap">{text}</span>
      </div>
    </div>
  );
};
