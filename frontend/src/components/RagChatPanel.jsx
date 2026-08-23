import React, { useState, useRef, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../hooks/useApi';
import Button from './Button';

export default function RagChatPanel({
  resourceId,
  resourceStatus = 'READY',
  onCitationClick,
}) {
  const { isAuthenticated } = useAuthStore();
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Hi! I am your StudyLink AI tutor scoped exclusively to this document. Ask any question regarding the notes or lectures above.',
      sources: [],
    },
  ]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const chatBottomRef = useRef(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputQuery.trim() || loading) return;

    if (!isAuthenticated) {
      setError('Please sign in to chat with notes.');
      return;
    }

    const userText = inputQuery.trim();
    setInputQuery('');
    setError('');

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userText,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await apiClient.post('/chat/query/', {
        resource_id: resourceId,
        query: userText,
      });

      const { answer, sources } = response.data;

      const assistantMessage = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: answer,
        sources: sources || [],
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error('RAG query error:', err);
      const errMsg =
        err.response?.data?.message ||
        'Unable to answer query. The document might not have enough context for this question.';
      setError(errMsg);
    } finally {
      setLoading(false);
    }
  };

  const isChatEnabled = resourceStatus === 'READY';

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden min-h-[600px] lg:min-h-[720px]">
      {/* Panel Header */}
      <div className="bg-slate-50/80 px-4 py-3.5 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-primary animate-pulse"></span>
          <h3 className="font-bold text-slate-800 text-sm tracking-tight">
            Scoped AI Tutor
          </h3>
        </div>
        <span className="text-xxs font-bold uppercase tracking-wider text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md">
          Single-Doc RAG
        </span>
      </div>

      {/* Disabled / Status State Overlay */}
      {!isChatEnabled && (
        <div className="p-6 bg-amber-50/70 border-b border-amber-200 text-center text-xs text-amber-800">
          <p className="font-bold mb-1">
            {resourceStatus === 'PROCESSING'
              ? '⏳ Embedding Ingestion in Progress'
              : `⚠️ Document Status: ${resourceStatus}`}
          </p>
          <p className="text-amber-700 leading-relaxed">
            {resourceStatus === 'PROCESSING'
              ? 'This document is currently being extracted and vectorized. AI questioning will become available once status is READY.'
              : 'AI Chat is only enabled for documents in READY status.'}
          </p>
        </div>
      )}

      {/* Messages Scroll Area */}
      <div className="flex-grow p-4 space-y-4 overflow-y-auto max-h-[500px] lg:max-h-[580px]">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${
              msg.role === 'user' ? 'items-end' : 'items-start'
            }`}
          >
            <div
              className={`max-w-[90%] rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-primary to-primary-dark text-white rounded-br-none shadow-md shadow-primary/10'
                  : 'bg-slate-100 text-slate-800 rounded-bl-none border border-slate-200/60'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>

            {/* Citations below AI responses */}
            {msg.sources && msg.sources.length > 0 && (
              <div className="mt-2 space-y-1.5 w-full max-w-[90%]">
                <p className="text-xxs font-bold text-slate-400 uppercase tracking-wider">
                  Page Citations
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {msg.sources.map((src, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => {
                        if (onCitationClick && src.page_number) {
                          onCitationClick(src.page_number);
                        }
                      }}
                      className="group flex flex-col text-left p-2 rounded-xl bg-primary/5 hover:bg-primary/15 border border-primary/20 text-xs transition-all w-full"
                      title="Click to jump to this page in PDF viewer"
                    >
                      <div className="flex items-center justify-between text-xxs font-bold text-primary mb-0.5">
                        <span className="inline-flex items-center gap-1">
                          <span>📄 Page {src.page_number}</span>
                          <span className="text-slate-400 font-normal">
                            (Jump &rarr;)
                          </span>
                        </span>
                        {src.similarity_score && (
                          <span className="font-mono text-slate-400">
                            {Math.round(src.similarity_score * 100)}% match
                          </span>
                        )}
                      </div>
                      {src.excerpt && (
                        <p className="text-xxs text-slate-600 line-clamp-2 italic font-mono bg-white/70 p-1 rounded">
                          "{src.excerpt}"
                        </p>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex items-start">
            <div className="bg-slate-100 rounded-2xl rounded-bl-none px-4 py-3 text-xs text-slate-500 border border-slate-200/60 flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce"></span>
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce delay-100"></span>
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce delay-200"></span>
              <span className="ml-1 text-slate-400 font-medium">
                Searching document embeddings...
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xxs font-semibold text-rose-700">
            {error}
          </div>
        )}

        <div ref={chatBottomRef} />
      </div>

      {/* Input Query Bar */}
      <form
        onSubmit={handleSend}
        className="p-3 border-t border-slate-100 bg-slate-50/50 flex items-center gap-2"
      >
        <input
          type="text"
          disabled={!isChatEnabled || loading}
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder={
            isChatEnabled
              ? 'Ask about concepts, proofs, formulas...'
              : 'Chat unavailable until document is READY'
          }
          className="flex-grow px-3.5 py-2.5 rounded-xl border border-slate-200 bg-white text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:bg-slate-100 disabled:cursor-not-allowed"
        />
        <Button
          type="submit"
          variant="primary"
          size="sm"
          disabled={!isChatEnabled || loading || !inputQuery.trim()}
          className="px-4 py-2.5"
        >
          Send
        </Button>
      </form>
    </div>
  );
}
