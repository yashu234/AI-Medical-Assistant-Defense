import React from 'react';
import { Sparkles, Stethoscope, UserCheck, AlertOctagon, FileText } from 'lucide-react';

const PROMPTS = [
  {
    icon: Stethoscope,
    label: 'Symptom Check',
    text: "I've had a dry cough and mild headache for 2 days. What should I monitor?",
    badge: 'Symptom',
    color: 'hover:border-teal-500 hover:bg-teal-50/50',
  },
  {
    icon: UserCheck,
    label: 'Specialist Finder',
    text: 'What kind of doctor should I consult for persistent knee clicking and stiffness?',
    badge: 'Specialist',
    color: 'hover:border-indigo-500 hover:bg-indigo-50/50',
  },
  {
    icon: Sparkles,
    label: 'Health Education',
    text: 'What is the physiological difference between LDL and HDL cholesterol?',
    badge: 'General',
    color: 'hover:border-blue-500 hover:bg-blue-50/50',
  },
  {
    icon: AlertOctagon,
    label: 'Emergency Safety Test',
    text: "I'm experiencing severe crushing chest pain radiating down my left arm.",
    badge: 'Red-Flag Test',
    color: 'hover:border-red-500 hover:bg-red-50/50 text-red-900',
  },
];

export default function QuickPrompts({ onSelectPrompt, onOpenPdfModal }) {
  return (
    <div className="max-w-4xl mx-auto my-6 px-4">
      <div className="text-center mb-5">
        <h2 className="text-lg sm:text-xl font-bold text-navy-900">
          Agentic Healthcare Assistance Demonstration
        </h2>
        <p className="text-xs sm:text-sm text-slate-500 max-w-xl mx-auto mt-1">
          Explore transparent intent routing, non-definitive symptom guidance, specialist matching, and strict emergency triage.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {PROMPTS.map((p, idx) => {
          const Icon = p.icon;
          return (
            <button
              key={idx}
              onClick={() => onSelectPrompt(p.text)}
              className={`flex items-start gap-3 text-left p-3 rounded-xl border border-slate-200 bg-white transition shadow-sm ${p.color}`}
            >
              <div className="p-2 rounded-lg bg-slate-100 text-slate-700 flex-shrink-0 mt-0.5">
                <Icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-1 mb-1">
                  <span className="text-xs font-semibold text-slate-900">{p.label}</span>
                  <span className="text-[10px] font-mono font-medium px-1.5 py-0.2 rounded bg-slate-100 text-slate-600">
                    {p.badge}
                  </span>
                </div>
                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                  "{p.text}"
                </p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
