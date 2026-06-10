import React from "react";

interface FollowUpPromptProps {
  missingFields: string[];
  onClickField: (field: string) => void;
}

export const FollowUpPrompt: React.FC<FollowUpPromptProps> = ({ missingFields, onClickField }) => {
  if (missingFields.length === 0) return null;

  return (
    <div className="p-3 bg-blue-50/50 border border-blue-100 rounded-2xl flex flex-wrap gap-2 text-xs font-semibold items-center">
      <span className="text-blue-800">Missing details:</span>
      {missingFields.map((field) => (
        <button
          key={field}
          onClick={() => onClickField(field)}
          className="px-2 py-1 bg-white hover:bg-blue-600 hover:text-white border border-blue-200 text-blue-600 rounded-full transition-all duration-200"
        >
          ➕ Add {field}
        </button>
      ))}
    </div>
  );
};
