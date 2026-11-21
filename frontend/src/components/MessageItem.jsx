import React from 'react';
import { User, Bot, AlertTriangle, Cpu, Tag } from 'lucide-react';
import EmergencyAlert from './EmergencyAlert';

const ROUTE_LABELS = {
  symptom_guidance: { label: 'Symptom Guidance', bg: 'bg-teal-100 text-teal-800 border-teal-200' },
  report_summary: { label: 'Report Summary', bg: 'bg-blue-100 text-blue-800 border-blue-200' },
  specialist_recommend: { label: 'Specialist Finder', bg: 'bg-indigo-100 text-indigo-800 border-indigo-200' },
  general_chat: { label: 'General Health Q&A', bg: 'bg-slate-100 text-slate-800 border-slate-200' },
  emergency_triage: { label: 'Emergency Red-Flag', bg: 'bg-red-100 text-red-800 border-red-300' },
};

function formatTextContent(text) {
  if (!text) return null;

  // Split lines and render simple markdown-like formatting
  return text.split('\n').map((line, idx) => {
    // Bold formatting: **text**
    const parts = line.split(/(\*\*.*?\*\*)/g);
    const formattedLine = parts.map((part, pIdx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={pIdx} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>;
      }
      return part;
    });

    if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
      return (
        <li key={idx} className="ml-4 list-disc text-slate-700 my-0.5 leading-relaxed">
          {formattedLine}
        </li>
      );
    }

    if (line.trim() === '') {
      return <div key={idx} className="h-2" />;
    }

    return (
      <p key={idx} className="my-1 leading-relaxed text-slate-800">
        {formattedLine}
      </p>
    );
  });
}

export default function MessageItem({ message }) {
  const isUser = message.role === 'user';
  const isEmergency = message.is_emergency;
  const routeMeta = ROUTE_LABELS[message.route] || null;

  if (isEmergency && !isUser) {
    return (
      <div className="my-2">
        <EmergencyAlert
          emergencyCategory={message.metadata?.category || 'Urgent Triage'}
          guidanceMessage={message.content}
        />
      </div>
    );
  }

  return (
    <div className={`flex gap-3 my-3 sm:my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-teal-600 text-white flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
          <Bot className="w-4 h-4" />
        </div>
      )}

      <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 shadow-sm ${
        isUser
          ? 'bg-navy-900 text-white rounded-tr-none'
          : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
      }`}>
        {/* Route / Metadata Badges for Assistant */}
        {!isUser && (
          <div className="flex flex-wrap items-center gap-1.5 mb-2 pb-2 border-b border-slate-100 text-[11px]">
            {routeMeta && (
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-medium border ${routeMeta.bg}`}>
                <Tag className="w-3 h-3" />
                Route: {routeMeta.label}
              </span>
            )}

            {message.is_simulated && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-mono bg-amber-50 text-amber-800 border border-amber-200">
                <Cpu className="w-3 h-3 text-amber-600" />
                Simulated Demo Engine
              </span>
            )}
          </div>
        )}

        {/* Message Body */}
        <div className={`text-sm ${isUser ? 'text-slate-100' : 'text-slate-800'}`}>
          {isUser ? (
            <p className="whitespace-pre-line leading-relaxed">{message.content}</p>
          ) : (
            <div>{formatTextContent(message.content)}</div>
          )}
        </div>

        {/* Timestamp */}
        <div className={`text-[10px] mt-2 font-mono ${isUser ? 'text-slate-400 text-right' : 'text-slate-400'}`}>
          {new Date(message.timestamp ? message.timestamp * 1000 : Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-300 text-slate-700 flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}
