import React, { useState } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { uploadReportPdf, summarizeReportText } from '../services/api';

const SYNTHETIC_SAMPLE_TEXT = `SYNTHETIC DEMO LABORATORY REPORT
Patient: Synthetic Demo Patient (ID: SYN-98241)
Date: 2026-11-15 | Specimen: Routine Blood Draw

COMPLETE BLOOD COUNT (CBC):
- White Blood Cells (WBC): 6.8 x10^3/uL (Reference: 4.5 - 11.0) [Normal]
- Red Blood Cells (RBC): 4.75 x10^6/uL (Reference: 4.30 - 5.90) [Normal]
- Hemoglobin: 14.2 g/dL (Reference: 13.5 - 17.5) [Normal]
- Platelets: 245 x10^3/uL (Reference: 150 - 450) [Normal]

COMPREHENSIVE METABOLIC PANEL (CMP):
- Glucose (Fasting): 94 mg/dL (Reference: 70 - 99) [Normal]
- Creatinine: 0.92 mg/dL (Reference: 0.60 - 1.20) [Normal]
- eGFR: >60 mL/min [Normal]
- Sodium: 139 mmol/L (Reference: 135 - 145) [Normal]

LIPID PANEL:
- Total Cholesterol: 208 mg/dL (Reference: <200 Desirable) [Borderline]
- Triglycerides: 145 mg/dL (Reference: <150 Normal) [Normal]
- HDL Cholesterol: 52 mg/dL (Reference: >40) [Normal]
- LDL Cholesterol: 127 mg/dL (Reference: <100 Optimal) [Above Optimal]

NOTE: Educational demonstration only. Discuss borderline cholesterol with primary care clinician.`;

export default function PdfUploadModal({ isOpen, onClose, sessionId, onReportProcessed }) {
  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setErrorMsg(null);
    if (!selected) return;

    if (!selected.name.toLowerCase().endsWith('.pdf')) {
      setErrorMsg('Only PDF documents (.pdf) are supported.');
      return;
    }

    if (selected.size > 5 * 1024 * 1024) {
      setErrorMsg('File exceeds 5MB size limit.');
      return;
    }

    setFile(selected);
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsProcessing(true);
    setErrorMsg(null);
    setUploadProgress(10);

    try {
      const response = await uploadReportPdf({
        file,
        sessionId,
        onProgress: (p) => setUploadProgress(p),
      });

      onReportProcessed(response, file.name);
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to process PDF report.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLoadSyntheticSample = async () => {
    setIsProcessing(true);
    setErrorMsg(null);
    setUploadProgress(50);

    try {
      const response = await summarizeReportText({
        reportText: SYNTHETIC_SAMPLE_TEXT,
        sessionId,
      });

      onReportProcessed(response, 'Synthetic Blood Test Report (CBC & Lipid Panel)');
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to process sample report.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 relative animate-in fade-in zoom-in-95 duration-150">
        <button
          onClick={onClose}
          disabled={isProcessing}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-9 h-9 rounded-lg bg-teal-100 text-teal-800 flex items-center justify-center">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 text-base">Medical Report Explainer</h3>
            <p className="text-xs text-slate-500">PDF text extraction and plain-language summary</p>
          </div>
        </div>

        {/* Safety Notice regarding PDF Input */}
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-600 mb-4">
          <p className="font-semibold text-slate-800 mb-0.5">Untrusted Document Notice:</p>
          Uploaded documents are sanitized and analyzed for educational explanation only.
          This is not clinical laboratory interpretation or diagnostic validation.
        </div>

        {/* File Dropzone */}
        <div className="border-2 border-dashed border-slate-300 hover:border-teal-500 rounded-xl p-6 text-center bg-slate-50 transition cursor-pointer mb-4">
          <input
            type="file"
            id="pdf-input"
            accept=".pdf"
            onChange={handleFileChange}
            disabled={isProcessing}
            className="hidden"
          />
          <label htmlFor="pdf-input" className="cursor-pointer flex flex-col items-center">
            <UploadCloud className="w-10 h-10 text-teal-600 mb-2" />
            <span className="text-sm font-medium text-slate-800">
              {file ? file.name : 'Select or drag a PDF document'}
            </span>
            <span className="text-xs text-slate-500 mt-1">
              {file ? `${(file.size / 1024).toFixed(1)} KB` : 'Maximum file size: 5MB'}
            </span>
          </label>
        </div>

        {/* Progress Bar */}
        {isProcessing && (
          <div className="mb-4">
            <div className="flex justify-between text-xs text-slate-500 mb-1">
              <span>Extracting & analyzing...</span>
              <span>{uploadProgress}%</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div
                className="bg-teal-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error Alert */}
        {errorMsg && (
          <div className="flex items-start gap-2 bg-red-50 text-red-800 p-3 rounded-lg text-xs mb-4 border border-red-200">
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
            <span className="leading-tight">{errorMsg}</span>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-2.5">
          <button
            onClick={handleUpload}
            disabled={!file || isProcessing}
            className={`flex-1 py-2 px-4 rounded-lg font-medium text-xs sm:text-sm transition flex items-center justify-center gap-2 ${
              !file || isProcessing
                ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                : 'bg-teal-600 hover:bg-teal-700 text-white shadow-sm'
            }`}
          >
            Upload & Summarize
          </button>

          <button
            onClick={handleLoadSyntheticSample}
            disabled={isProcessing}
            className="py-2 px-3 bg-navy-900 hover:bg-navy-800 text-teal-300 border border-teal-500/30 rounded-lg font-medium text-xs sm:text-sm transition flex items-center justify-center gap-1.5"
            title="Load synthetic lab report without uploading local files"
          >
            <Sparkles className="w-4 h-4 text-teal-400" />
            Load Synthetic Sample
          </button>
        </div>
      </div>
    </div>
  );
}
