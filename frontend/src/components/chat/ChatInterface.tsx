import React, { useState, useRef, useEffect } from "react";
import { usePlanning } from "../../hooks/usePlanning";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { FollowUpPrompt } from "./FollowUpPrompt";

export const ChatInterface: React.FC = () => {
  const [text, setText] = useState("");
  const { messages, loading, missingfields, sendMessage, editTrip, tripData } = usePlanning();
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!text.trim()) return;
    const msg = text;
    setText("");
    await sendMessage(msg);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[600px] border border-gray-100 rounded-3xl bg-white shadow-xl overflow-hidden">
      <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-4 text-white font-bold flex items-center justify-between">
        <span className="flex items-center gap-2">💬 AI Travel Assistant</span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50/50">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} role={msg.role} text={msg.text} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={chatEndRef} />
      </div>

      <div className="p-4 bg-white border-t border-gray-100 space-y-3">
        <FollowUpPrompt
          missingFields={missingfields}
          onClickField={(field) => {
            setText(`My ${field} is: `);
          }}
        />
        <div className="flex gap-2 items-center">
          <textarea
            className="flex-1 px-4 py-2 border border-gray-200 rounded-2xl outline-none resize-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 transition-all text-sm h-12"
            placeholder={tripData ? "Modify itinerary (e.g. swap day 2 morning)..." : "Plan a trip to Tokyo..."}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="px-5 h-12 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-2xl shadow-md transition-all duration-300 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};
