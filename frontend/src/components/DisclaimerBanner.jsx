import React from 'react';
import { AlertTriangle, ShieldCheck, Activity } from 'lucide-react';

export default function DisclaimerBanner({ backendHealth }) {
  const isSimulated = backendHealth?.mode?.includes('Simulated');
  const isHealthy = backendHealth?.status === 'healthy';

  return (
    <div className="bg-amber-50 border-b border-amber-200 text-amber-900 px-4 py-2.5 text-xs sm:text-sm">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-2">
        <div className="flex items-start sm:items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5 sm:mt-0" />
          <p className="font-medium leading-tight">
            <span className="font-bold uppercase tracking-wider text-[11px] bg-amber-200/80 text-amber-950 px-1.5 py-0.5 rounded mr-1.5">
              Notice
            </span>
            Educational demo only. Not medical advice. For urgent or severe symptoms, contact local emergency services or a qualified healthcare professional.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs flex-shrink-0 self-end md:self-center">
          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full font-medium ${
            isHealthy ? 'bg-teal-100 text-teal-800' : 'bg-red-100 text-red-800'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${isHealthy ? 'bg-teal-600 animate-pulse' : 'bg-red-600'}`} />
            {isHealthy ? 'System Active' : 'Connecting...'}
          </span>

          <span className="inline-flex items-center gap-1 bg-slate-200/80 text-slate-700 px-2 py-0.5 rounded-full font-mono text-[11px]">
            {isSimulated ? 'Local Simulated Mode' : 'OpenAI Connected'}
          </span>
        </div>
      </div>
    </div>
  );
}
