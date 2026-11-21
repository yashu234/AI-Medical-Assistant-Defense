import React from 'react';
import { HeartPulse, PlusCircle, Trash2, Cpu } from 'lucide-react';

export default function Header({ sessionId, onNewSession, onClearSession, backendHealth }) {
  return (
    <header className="bg-navy-900 text-white border-b border-navy-800 shadow-sm sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3.5 flex flex-wrap items-center justify-between gap-3">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-teal-600 flex items-center justify-center text-white shadow-md shadow-teal-900/30">
            <HeartPulse className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-semibold text-base sm:text-lg tracking-tight flex items-center gap-2">
              AI Medical Assistant
              <span className="text-[10px] uppercase font-mono font-bold tracking-widest bg-navy-800 text-teal-300 border border-teal-500/30 px-2 py-0.5 rounded">
                MVP Demo
              </span>
            </h1>
            <p className="text-xs text-slate-400">
              Agentic Healthcare Chatbot • Educational Demonstration
            </p>
          </div>
        </div>

        {/* Session Controls */}
        <div className="flex items-center gap-2 sm:gap-3 text-xs">
          <div className="hidden sm:flex flex-col items-end mr-1">
            <span className="text-[10px] text-slate-400 uppercase tracking-wider font-mono">Session ID</span>
            <span className="font-mono text-slate-200 text-xs truncate max-w-[140px]" title={sessionId}>
              {sessionId.substring(0, 16)}...
            </span>
          </div>

          <button
            onClick={onNewSession}
            title="Start a fresh conversation session"
            className="flex items-center gap-1.5 bg-teal-600 hover:bg-teal-700 active:bg-teal-800 text-white px-3 py-1.5 rounded-md font-medium transition shadow-sm"
          >
            <PlusCircle className="w-3.5 h-3.5" />
            <span className="hidden xs:inline">New Session</span>
          </button>

          <button
            onClick={onClearSession}
            title="Clear message history for current session"
            className="flex items-center gap-1.5 bg-navy-800 hover:bg-navy-700 text-slate-300 hover:text-white px-2.5 py-1.5 rounded-md transition border border-navy-700"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Clear</span>
          </button>
        </div>
      </div>
    </header>
  );
}
