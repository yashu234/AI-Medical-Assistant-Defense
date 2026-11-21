import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import DisclaimerBanner from './components/DisclaimerBanner';
import MessageItem from './components/MessageItem';
import ChatInput from './components/ChatInput';
import QuickPrompts from './components/QuickPrompts';
import PdfUploadModal from './components/PdfUploadModal';
import {
  checkBackendHealth,
  sendChatMessage,
  getSessionHistory,
  clearSessionHistory,
} from './services/api';

function generateSessionId() {
  return 'sess-' + Math.random().toString(36).substring(2, 10) + '-' + Date.now().toString(36);
}

export default function App() {
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem('ai_medical_session_id') || generateSessionId();
  });
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [backendHealth, setBackendHealth] = useState(null);
  const [isPdfModalOpen, setIsPdfModalOpen] = useState(false);
  const [errorToast, setErrorToast] = useState(null);

  const messagesEndRef = useRef(null);

  // Persist session ID
  useEffect(() => {
    localStorage.setItem('ai_medical_session_id', sessionId);
  }, [sessionId]);

  // Check health and load session history
  useEffect(() => {
    async function init() {
      const health = await checkBackendHealth();
      setBackendHealth(health);

      try {
        const hist = await getSessionHistory(sessionId);
        if (hist && hist.messages) {
          setMessages(hist.messages);
        }
      } catch (err) {
        console.warn('Could not load session history:', err);
      }
    }
    init();
  }, [sessionId]);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (userText, forceRoute = null) => {
    if (!userText.trim()) return;

    setErrorToast(null);

    // Optimistically add user message to list
    const userMsgObj = {
      role: 'user',
      content: userText,
      timestamp: Date.now() / 1000,
    };
    setMessages((prev) => [...prev, userMsgObj]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        message: userText,
        sessionId,
        forceRoute,
      });

      const assistantMsgObj = {
        role: 'assistant',
        content: response.message,
        route: response.detected_route,
        is_emergency: response.safety?.is_emergency || false,
        is_simulated: response.safety?.is_simulated || false,
        timestamp: Date.now() / 1000,
        metadata: response.metadata || {},
      };

      setMessages((prev) => [...prev, assistantMsgObj]);
    } catch (err) {
      setErrorToast(err.message || 'Error communicating with assistant.');
      // Remove optimistic message if failed completely or append error notice
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ Error: ${err.message || 'Unable to complete request. Please verify the backend is running.'}`,
          timestamp: Date.now() / 1000,
          metadata: { error: true },
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewSession = () => {
    const newId = generateSessionId();
    setSessionId(newId);
    setMessages([]);
    setErrorToast(null);
  };

  const handleClearSession = async () => {
    try {
      await clearSessionHistory(sessionId);
      setMessages([]);
      setErrorToast(null);
    } catch (err) {
      setErrorToast('Failed to clear session on server.');
    }
  };

  const handleReportProcessed = (reportResponse, filename) => {
    let formattedContent = `**Summary of Document: ${filename}**\n\n${reportResponse.summary}\n\n`;
    if (reportResponse.key_findings_explained?.length > 0) {
      formattedContent += `**Key Laboratory Findings Explained:**\n${reportResponse.key_findings_explained.map(f => `• ${f}`).join('\n')}\n\n`;
    }
    if (reportResponse.questions_for_doctor?.length > 0) {
      formattedContent += `**Suggested Questions for Your Physician:**\n${reportResponse.questions_for_doctor.map(q => `• ${q}`).join('\n')}\n\n`;
    }
    if (reportResponse.limitations_note) {
      formattedContent += `*${reportResponse.limitations_note}*`;
    }

    const reportMsg = {
      role: 'assistant',
      content: formattedContent,
      route: 'report_summary',
      is_emergency: reportResponse.safety?.is_emergency || false,
      is_simulated: reportResponse.safety?.is_simulated || false,
      timestamp: Date.now() / 1000,
      metadata: { file: filename },
    };

    setMessages((prev) => [...prev, reportMsg]);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Persistent Disclaimer Banner */}
      <DisclaimerBanner backendHealth={backendHealth} />

      {/* Main Header */}
      <Header
        sessionId={sessionId}
        onNewSession={handleNewSession}
        onClearSession={handleClearSession}
        backendHealth={backendHealth}
      />

      {/* Chat Area */}
      <main className="flex-1 max-w-4xl w-full mx-auto p-4 flex flex-col justify-between">
        <div className="flex-1 space-y-2">
          {/* Empty State Prompts */}
          {messages.length === 0 ? (
            <QuickPrompts
              onSelectPrompt={(text) => handleSendMessage(text)}
              onOpenPdfModal={() => setIsPdfModalOpen(true)}
            />
          ) : (
            messages.map((msg, idx) => <MessageItem key={idx} message={msg} />)
          )}

          {/* Loading Indicator */}
          {isLoading && (
            <div className="flex items-center gap-3 my-4">
              <div className="w-8 h-8 rounded-full bg-teal-600 text-white flex items-center justify-center animate-pulse">
                <span className="text-xs font-bold">AI</span>
              </div>
              <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm flex items-center gap-2 text-xs text-slate-500">
                <div className="w-2 h-2 rounded-full bg-teal-600 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-teal-600 animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 rounded-full bg-teal-600 animate-bounce [animation-delay:0.4s]" />
                <span className="ml-2 font-medium">Analyzing healthcare inquiry...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Error Toast */}
      {errorToast && (
        <div className="fixed bottom-24 left-1/2 -translate-x-1/2 bg-red-600 text-white text-xs px-4 py-2 rounded-full shadow-lg z-40 flex items-center gap-2">
          <span>{errorToast}</span>
          <button onClick={() => setErrorToast(null)} className="font-bold underline ml-1">
            Dismiss
          </button>
        </div>
      )}

      {/* Chat Input & Controls */}
      <ChatInput
        onSendMessage={handleSendMessage}
        onOpenPdfModal={() => setIsPdfModalOpen(true)}
        isLoading={isLoading}
      />

      {/* PDF Upload Modal */}
      <PdfUploadModal
        isOpen={isPdfModalOpen}
        onClose={() => setIsPdfModalOpen(false)}
        sessionId={sessionId}
        onReportProcessed={handleReportProcessed}
      />
    </div>
  );
}
