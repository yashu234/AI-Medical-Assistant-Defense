import React, { useState } from 'react';
import { Send, FileUp, Sparkles, Stethoscope, FileText, UserCheck, MessageSquare } from 'lucide-react';

const MODES = [
  { id: null, label: 'Auto-Detect Route', icon: Sparkles },
  { id: 'symptom_guidance', label: 'Symptom Check', icon: Stethoscope },
  { id: 'report_summary', label: 'Report Explainer', icon: FileText },
  { id: 'specialist_recommend', label: 'Specialist Finder', icon: UserCheck },
  { id: 'general_chat', label: 'General Health', icon: MessageSquare },
];

export default function ChatInput({ onSendMessage, onOpenPdfModal, isLoading }) {
  const [input, setInput] = useState('');
  const [selectedMode, setSelectedMode] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    onSendMessage(trimmed, selectedMode);
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="bg-white border-t border-slate-200 p-3 sm:p-4 shadow-lg sticky bottom-0 z-20">
      <div className="max-w-4xl mx-auto space-y-2.5">
        {/* Mode Selector Chips */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs no-scrollbar">
          <span className="text-[11px] font-medium text-slate-600 mr-1 flex-shrink-0">Mode:</span>
          {MODES.map((mode) => {
            const Icon = mode.icon;
            const isSelected = selectedMode === mode.id;
            return (
              <button
                key={mode.id || 'auto'}
                type="button"
                onClick={() => setSelectedMode(mode.id)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full font-medium transition flex-shrink-0 text-xs border ${
                  isSelected
                    ? 'bg-navy-900 text-teal-300 border-navy-900 shadow-sm'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-600 border-slate-200'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-teal-400' : 'text-slate-500'}`} />
                {mode.label}
              </button>
            );
          })}
        </div>

        {/* Input Textarea and Actions */}
        <form onSubmit={handleSubmit} className="relative flex items-end gap-2 bg-slate-50 border border-slate-300 rounded-xl p-1.5 focus-within:border-teal-600 focus-within:ring-1 focus-within:ring-teal-600 transition shadow-inner">
          <button
            type="button"
            onClick={onOpenPdfModal}
            title="Upload or analyze medical PDF report"
            className="p-2 text-slate-500 hover:text-teal-700 hover:bg-teal-50 rounded-lg transition flex items-center justify-center flex-shrink-0"
          >
            <FileUp className="w-5 h-5" />
          </button>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your health inquiry, describe symptoms, or ask about specialists..."
            rows={2}
            disabled={isLoading}
            className="flex-1 bg-transparent border-0 resize-none text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-0 py-1.5 px-1 max-h-32"
          />

          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`p-2.5 rounded-lg flex items-center justify-center transition flex-shrink-0 ${
              !input.trim() || isLoading
                ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                : 'bg-teal-600 hover:bg-teal-700 active:bg-teal-800 text-white shadow-sm'
            }`}
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>

        <p className="text-[11px] text-slate-600 text-center">
          Press <strong>Enter</strong> to send, <strong>Shift + Enter</strong> for newline. Do not enter real patient identifying data.
        </p>
      </div>
    </div>
  );
}
