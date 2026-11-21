import React from 'react';
import { AlertOctagon, PhoneCall, ShieldAlert } from 'lucide-react';

export default function EmergencyAlert({ emergencyCategory, guidanceMessage }) {
  return (
    <div className="bg-red-50 border-2 border-red-500 rounded-xl p-4 sm:p-5 my-4 text-red-950 shadow-md animate-pulse-subtle">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-full bg-red-600 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
          <AlertOctagon className="w-6 h-6" />
        </div>
        <div className="flex-1 space-y-2">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="font-bold text-red-900 text-base sm:text-lg flex items-center gap-2">
              EMERGENCY MEDICAL WARNING
            </h3>
            {emergencyCategory && (
              <span className="text-xs font-mono font-semibold bg-red-200 text-red-900 px-2 py-0.5 rounded">
                Category: {emergencyCategory}
              </span>
            )}
          </div>

          <p className="text-sm text-red-900 leading-relaxed font-medium whitespace-pre-line">
            {guidanceMessage || (
              "Your message suggests a potential medical emergency. Stop using this chatbot immediately and seek urgent emergency medical evaluation."
            )}
          </p>

          <div className="bg-white/80 border border-red-200 rounded-lg p-3 mt-3 text-xs space-y-1.5 text-red-950">
            <p className="font-bold flex items-center gap-1.5 text-red-800">
              <PhoneCall className="w-3.5 h-3.5 text-red-600" />
              Immediate Emergency Contact Resources:
            </p>
            <ul className="list-disc list-inside space-y-0.5 pl-1">
              <li><strong>United States / Canada:</strong> Call <strong>911</strong> or visit nearest Emergency Room.</li>
              <li><strong>United Kingdom:</strong> Call <strong>999</strong> or 111 for urgent advice.</li>
              <li><strong>Europe / India:</strong> Call <strong>112</strong> for emergency response.</li>
              <li><strong>Crisis & Suicide Lifeline:</strong> Call or text <strong>988</strong> (US/Canada) or text HOME to 741741.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
