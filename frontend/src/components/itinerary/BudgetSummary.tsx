import React from "react";
import { BudgetInfo } from "../../api/types";

interface BudgetSummaryProps {
  budget: BudgetInfo;
  totalLimit: number;
  totalCost: number;
  currency: string;
}

export const BudgetSummary: React.FC<BudgetSummaryProps> = ({ budget, totalLimit, totalCost, currency }) => {
  const percentUsed = Math.min(100, Math.round((totalCost / totalLimit) * 100));
  const currSym = currency || budget.currency || "$";
  
  const formatVal = (val: number) => {
    return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(val);
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-100 p-8 rounded-3xl border border-indigo-200 shadow-md">
      <h3 className="text-2xl font-extrabold text-indigo-900 mb-6 flex items-center gap-2">
        💰 Trip Budget Intelligence
      </h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-gray-800 mb-6">
        <div className="bg-white p-5 rounded-2xl shadow-sm flex flex-col justify-center min-w-0 border border-gray-100">
          <span className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1 truncate">Total Limit</span>
          <span 
            className="text-base sm:text-lg lg:text-xl font-extrabold text-indigo-700 block whitespace-nowrap overflow-x-auto" 
            style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
            title={`${currSym} ${formatVal(totalLimit)}`}
          >
            {currSym} {formatVal(totalLimit)}
          </span>
        </div>
        <div className="bg-white p-5 rounded-2xl shadow-sm flex flex-col justify-center min-w-0 border border-gray-100">
          <span className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1 truncate">Total Est. Cost</span>
          <span 
            className="text-base sm:text-lg lg:text-xl font-extrabold text-blue-700 block whitespace-nowrap overflow-x-auto"
            style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
            title={`${currSym} ${formatVal(totalCost)}`}
          >
            {currSym} {formatVal(totalCost)}
          </span>
        </div>
        <div className="bg-white p-5 rounded-2xl shadow-sm flex flex-col justify-center min-w-0 border border-gray-100">
          <span className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1 truncate">Remaining</span>
          <span 
            className="text-base sm:text-lg lg:text-xl font-extrabold text-purple-700 block whitespace-nowrap overflow-x-auto"
            style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
            title={`${currSym} ${formatVal(Math.max(0, totalLimit - totalCost))}`}
          >
            {currSym} {formatVal(Math.max(0, totalLimit - totalCost))}
          </span>
        </div>
        <div className="bg-white p-5 rounded-2xl shadow-sm flex flex-col justify-center min-w-0 border border-gray-100">
          <span className="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1 truncate">Budget Score</span>
          <span 
            className="text-base sm:text-lg lg:text-xl font-extrabold text-emerald-700 block whitespace-nowrap overflow-x-auto"
            style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
          >
            {budget.score} / 10.0
          </span>
        </div>
      </div>

      <div className="space-y-2 mb-6">
        <div className="flex justify-between text-sm text-indigo-950 font-semibold">
          <span>Used Budget</span>
          <span>{percentUsed}%</span>
        </div>
        <div className="w-full bg-gray-200 h-3 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-1000"
            style={{ width: `${percentUsed}%` }}
          ></div>
        </div>
      </div>

      {budget.warnings && budget.warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 p-4 rounded-2xl text-sm">
          <h4 className="font-bold mb-1">⚠️ Budget Alerts</h4>
          <ul className="list-disc pl-4 space-y-1">
            {budget.warnings.map((warn, idx) => (
              <li key={idx}>{warn}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
