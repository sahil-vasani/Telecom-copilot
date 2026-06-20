import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, Copy, Check, Info, ShieldAlert, CheckCircle, 
  ExternalLink, Clock, Server, CheckSquare, ChevronRight, ChevronDown, ListRestart
} from 'lucide-react';
import { sendChatMessage } from '../services/api';
import { Message, Citation, RetrievedDocument, ToolTrace } from '../types';
import { formatLatency, cn } from '../utils/helpers';

const SUGGESTED_QUESTIONS = [
  "How do I dispute a wrong charge on my Airtel bill?",
  "My 4G is not working in Mumbai since this morning.",
  "I was charged Rs. 12,000 for roaming on a 2-day trip.",
  "Can I downgrade my postpaid plan this month?",
  "How do I switch my physical SIM to eSIM?"
];

const Copilot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hello! I am TelecomRAG Copilot, your carrier operations agent. Ask me about bill disputes, billing charges, policy details, or live network health status.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [activeMessage, setActiveMessage] = useState<Message | null>(null);
  const [citationModal, setCitationModal] = useState<Citation | null>(null);
  const [expandedDocs, setExpandedDocs] = useState<Record<string, boolean>>({});

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Set the selected message for right panel telemetry
  useEffect(() => {
    const assistantMsgs = messages.filter(m => m.role === 'assistant' && !m.isLoading);
    if (assistantMsgs.length > 0) {
      setActiveMessage(assistantMsgs[assistantMsgs.length - 1]);
    }
  }, [messages]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMsgId = Math.random().toString(36).substring(7);
    const assistantMsgId = Math.random().toString(36).substring(7);
    const nowStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const newUserMsg: Message = {
      id: userMsgId,
      role: 'user',
      content: text,
      timestamp: nowStr
    };

    const newAssistantMsgPlaceholder: Message = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      timestamp: nowStr,
      isLoading: true
    };

    setMessages(prev => [...prev, newUserMsg, newAssistantMsgPlaceholder]);
    setInputValue('');

    try {
      // Build history payload
      const history = messages
        .filter(m => m.id !== 'welcome' && !m.isLoading && !m.error)
        .map(m => ({
          role: m.role === 'user' ? 'user' : 'agent',
          utterance: m.content
        }));

      const res = await sendChatMessage(text, history);

      setMessages(prev => 
        prev.map(m => 
          m.id === assistantMsgId 
            ? {
                ...m,
                content: res.answer,
                citations: res.citations,
                toolTrace: res.tool_trace,
                confidence: res.confidence,
                escalated: res.escalated,
                ticketId: res.ticket_id,
                retrieved: res.retrieved,
                latencyMs: res.latency_ms,
                isLoading: false
              }
            : m
        )
      );
    } catch (err: any) {
      setMessages(prev => 
        prev.map(m => 
          m.id === assistantMsgId 
            ? {
                ...m,
                content: "I encountered an error executing the query loop.",
                isLoading: false,
                error: err.message || "Unknown retrieval error"
              }
            : m
        )
      );
    }
  };

  const copyToClipboard = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleDocExpand = (docId: string, sectionId: string) => {
    const key = `${docId}_${sectionId}`;
    setExpandedDocs(prev => ({ ...prev, [key]: !prev[key] }));
  };

  // Renders message content and highlights sources inline
  const renderMessageContent = (msg: Message) => {
    if (msg.isLoading) {
      return (
        <div className="flex items-center gap-1.5 py-2 px-1">
          <div className="h-2 w-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="h-2 w-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="h-2 w-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      );
    }

    if (msg.error) {
      return (
        <div className="flex items-start gap-2 text-error">
          <ShieldAlert className="h-5 w-5 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-sm">System Out-of-Scope / Connection Error</p>
            <p className="text-xs text-error/85">{msg.error}</p>
          </div>
        </div>
      );
    }

    // Split text by citations e.g. [SOURCE: doc, section]
    const text = msg.content;
    const parts = text.split(/(\[SOURCE:\s*[^,\]]+,\s*[^\]]+\])/g);

    return (
      <p className="text-sm leading-relaxed whitespace-pre-wrap">
        {parts.map((part, index) => {
          const citationMatch = part.match(/\[SOURCE:\s*([^,\]]+),\s*([^\]]+)\]/);
          if (citationMatch) {
            const docId = citationMatch[1].trim();
            const sectionId = citationMatch[2].trim();
            return (
              <button
                key={index}
                onClick={() => {
                  const citationObj = msg.citations?.find(c => c.doc_id === docId && c.section_id === sectionId);
                  setCitationModal(citationObj || { doc_id: docId, section_id: sectionId });
                }}
                className="inline-flex items-center gap-0.5 px-1.5 py-0.5 mx-0.5 text-[10px] font-bold font-mono bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 rounded transition-colors"
              >
                Cite: {docId.substring(0, 12)}...
              </button>
            );
          }
          return part;
        })}
      </p>
    );
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-10 gap-6 h-[calc(100vh-100px)] overflow-hidden">
      {/* LEFT CHAT PANEL (70%) */}
      <div className="lg:col-span-7 flex flex-col h-full glass-panel rounded-2xl overflow-hidden">
        {/* Chat screen window */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                onClick={() => msg.role === 'assistant' && !msg.isLoading && setActiveMessage(msg)}
                className={cn(
                  "flex flex-col max-w-[85%] rounded-2xl p-4 border transition-all cursor-pointer",
                  msg.role === 'user'
                    ? "ml-auto bg-primary/5 border-primary/20 text-textPrimary"
                    : cn(
                        "bg-slate-900/40 border-borderDark hover:border-slate-700",
                        activeMessage?.id === msg.id && "border-primary/40 ring-1 ring-primary/20 bg-slate-900/60 shadow-[0_0_15px_rgba(0,229,255,0.05)]"
                      )
                )}
              >
                <div className="flex items-center justify-between gap-6 mb-2 border-b border-white/5 pb-1">
                  <span className={cn(
                    "text-[10px] font-mono uppercase tracking-wider font-semibold",
                    msg.role === 'user' ? "text-primary" : "text-emerald-400"
                  )}>
                    {msg.role === 'user' ? 'Operator' : 'TelecomRAG Copilot'}
                  </span>
                  <span className="text-[10px] text-textSecondary">{msg.timestamp}</span>
                </div>

                <div className="text-textPrimary text-left">
                  {renderMessageContent(msg)}
                </div>

                {msg.role === 'assistant' && !msg.isLoading && !msg.error && (
                  <div className="flex items-center justify-between gap-4 mt-3 pt-2 border-t border-white/5">
                    {/* Citations list view inside bubble */}
                    <div className="flex flex-wrap gap-1">
                      {msg.citations?.map((c, i) => (
                        <span key={i} className="px-1.5 py-0.5 text-[9px] font-mono font-medium bg-slate-800 rounded border border-borderDark text-textSecondary">
                          {c.doc_id}
                        </span>
                      ))}
                    </div>

                    {/* Copy action */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        copyToClipboard(msg.id, msg.content);
                      }}
                      className="p-1 text-textSecondary hover:text-textPrimary hover:bg-white/5 rounded transition-colors"
                      title="Copy response"
                    >
                      {copiedId === msg.id ? <Check className="h-4 w-4 text-success" /> : <Copy className="h-4 w-4" />}
                    </button>
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={chatEndRef} />
        </div>

        {/* Suggestion & input box */}
        <div className="p-4 border-t border-borderDark bg-surface/20 space-y-3">
          {/* Suggested prompts list */}
          {messages.length === 1 && (
            <div className="flex flex-wrap gap-2 px-2">
              {SUGGESTED_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(q)}
                  className="px-3 py-1.5 text-xs text-textSecondary hover:text-primary hover:border-primary/40 bg-slate-950/40 hover:bg-primary/5 border border-borderDark rounded-full transition-all text-left truncate max-w-full"
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {/* Form */}
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(inputValue);
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask Copilot (e.g. 'Outage check in Mumbai' or 'Billing discrepancy Rs. 12000')"
              className="flex-1 px-4 py-3 rounded-xl glass-input text-sm text-textPrimary"
            />
            <button
              type="submit"
              disabled={!inputValue.trim()}
              className="p-3 bg-primary text-background hover:bg-primary/95 disabled:opacity-50 disabled:hover:bg-primary font-bold rounded-xl transition-all shadow-[0_0_15px_rgba(0,229,255,0.25)] shrink-0"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>

      {/* RIGHT INSIGHTS PANEL (30%) */}
      <div className="lg:col-span-3 flex flex-col gap-6 overflow-y-auto pr-1">
        {activeMessage ? (
          <>
            {/* 1. Confidence & Telemetry Card */}
            <div className="glass-panel p-5 rounded-2xl relative overflow-hidden">
              <h2 className="text-xs font-bold text-textSecondary uppercase tracking-widest mb-4 flex items-center gap-2">
                <Info className="h-4 w-4 text-primary" />
                <span>Confidence & Latency</span>
              </h2>

              <div className="flex items-center justify-between gap-4">
                {/* Confidence circle */}
                <div className="flex flex-col items-center">
                  <div className="relative flex items-center justify-center h-20 w-20">
                    <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                      <path
                        className="text-slate-800"
                        strokeWidth="3.5"
                        stroke="currentColor"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      <path
                        className={cn(
                          "transition-all duration-1000",
                          (activeMessage.confidence || 0) > 0.85 ? "text-primary" : "text-warning"
                        )}
                        strokeWidth="3.5"
                        strokeDasharray={`${(activeMessage.confidence || 0) * 100}, 100`}
                        strokeLinecap="round"
                        stroke="currentColor"
                        fill="none"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                    <span className="absolute text-sm font-bold font-mono">
                      {((activeMessage.confidence || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                  <span className="text-[10px] text-textSecondary mt-2">Confidence Match</span>
                </div>

                {/* Telemetry numbers */}
                <div className="flex-1 space-y-3 font-mono">
                  <div className="bg-slate-950/45 p-2 rounded-lg border border-borderDark flex items-center justify-between">
                    <span className="text-[10px] text-textSecondary">Latency</span>
                    <span className="text-xs font-semibold text-primary flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatLatency(activeMessage.latencyMs)}
                    </span>
                  </div>

                  <div className="bg-slate-950/45 p-2 rounded-lg border border-borderDark flex items-center justify-between">
                    <span className="text-[10px] text-textSecondary">Escalated</span>
                    <span className={cn(
                      "text-xs font-semibold px-2 py-0.5 rounded text-[10px]",
                      activeMessage.escalated ? "bg-error/15 text-error border border-error/20" : "bg-success/15 text-success border border-success/20"
                    )}>
                      {activeMessage.escalated ? 'TRUE' : 'FALSE'}
                    </span>
                  </div>
                </div>
              </div>

              {activeMessage.ticketId && (
                <div className="mt-4 p-3 bg-error/5 border border-error/15 rounded-xl flex items-center justify-between">
                  <div>
                    <p className="text-[10px] text-error font-bold uppercase tracking-wider">Escalation ticket</p>
                    <p className="text-xs font-mono font-semibold text-textPrimary mt-0.5">{activeMessage.ticketId}</p>
                  </div>
                  <CheckSquare className="h-5 w-5 text-error shrink-0" />
                </div>
              )}
            </div>

            {/* 2. Tool Execution Timeline */}
            <div className="glass-panel p-5 rounded-2xl">
              <h2 className="text-xs font-bold text-textSecondary uppercase tracking-widest mb-4 flex items-center gap-2">
                <Server className="h-4 w-4 text-primary" />
                <span>Tool execution flow</span>
              </h2>

              <div className="space-y-4 relative before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-[1px] before:bg-borderDark">
                {(activeMessage.toolTrace || []).length > 0 ? (
                  activeMessage.toolTrace?.map((trace, idx) => (
                    <div key={idx} className="flex gap-4 relative">
                      <div className="z-10 flex items-center justify-center h-7 w-7 rounded-full bg-slate-900 border border-primary/40 text-primary text-xs font-mono shrink-0">
                        {idx + 1}
                      </div>
                      <div className="bg-slate-950/45 border border-borderDark p-3 rounded-xl flex-1 text-left font-mono">
                        <p className="text-xs font-bold text-textPrimary">{trace.tool}</p>
                        <p className="text-[9px] text-textSecondary mt-1 leading-snug">
                          {trace.output_summary}
                        </p>
                        {Object.keys(trace.params).length > 0 && (
                          <div className="mt-2 text-[8px] text-primary/80 bg-slate-900 p-1.5 rounded border border-borderDark leading-tight overflow-x-auto whitespace-pre">
                            {JSON.stringify(trace.params, null, 2)}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-xs text-textSecondary py-4 pl-6">No tool calls requested.</div>
                )}
              </div>
            </div>

            {/* 3. Retrieved Evidence */}
            <div className="glass-panel p-5 rounded-2xl">
              <h2 className="text-xs font-bold text-textSecondary uppercase tracking-widest mb-4">
                Retrieved Documents ({(activeMessage.retrieved || []).length})
              </h2>

              <div className="space-y-3">
                {(activeMessage.retrieved || []).map((doc, idx) => {
                  const expandKey = `${doc.doc_id}_${doc.section_id}`;
                  const isExpanded = !!expandedDocs[expandKey];
                  return (
                    <div 
                      key={idx}
                      className="bg-slate-950/45 border border-borderDark rounded-xl overflow-hidden transition-all text-left"
                    >
                      <button
                        onClick={() => toggleDocExpand(doc.doc_id, doc.section_id)}
                        className="w-full p-3 flex items-center justify-between gap-3 text-xs font-mono text-textPrimary hover:bg-white/5"
                      >
                        <div className="truncate flex-1">
                          <p className="font-semibold truncate">{doc.doc_id}</p>
                          <p className="text-[10px] text-textSecondary truncate">{doc.heading}</p>
                        </div>
                        <div className="flex items-center gap-2 shrink-0">
                          <span className="text-[10px] text-primary">Score: {doc.dense_score.toFixed(4)}</span>
                          {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                        </div>
                      </button>

                      {isExpanded && (
                        <div className="p-3 border-t border-borderDark bg-slate-900/35 text-[10px] text-textSecondary font-mono leading-relaxed max-h-48 overflow-y-auto">
                          {doc.text}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        ) : (
          <div className="glass-panel p-6 rounded-2xl text-center text-xs text-textSecondary flex flex-col items-center justify-center gap-3 h-64">
            <ListRestart className="h-8 w-8 text-textSecondary/50 animate-spin-slow" />
            <p>Waiting for agent query context...</p>
          </div>
        )}
      </div>

      {/* CITATION MODAL DIALOG */}
      {citationModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="glass-panel w-full max-w-xl rounded-2xl overflow-hidden shadow-2xl border border-primary/20">
            <div className="px-6 py-4 border-b border-borderDark flex items-center justify-between bg-surface/50">
              <h3 className="text-sm font-bold font-mono text-primary flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-primary" />
                <span>Citation Inspector</span>
              </h3>
              <button 
                onClick={() => setCitationModal(null)}
                className="text-textSecondary hover:text-textPrimary text-xs hover:bg-white/5 px-2.5 py-1 rounded-lg transition-colors border border-borderDark"
              >
                Close
              </button>
            </div>
            
            <div className="p-6 text-left space-y-4">
              <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                <div className="bg-slate-950/50 p-3 border border-borderDark rounded-xl">
                  <p className="text-[10px] text-textSecondary">Document ID</p>
                  <p className="font-semibold mt-1 text-textPrimary">{citationModal.doc_id}</p>
                </div>
                <div className="bg-slate-950/50 p-3 border border-borderDark rounded-xl">
                  <p className="text-[10px] text-textSecondary">Section ID</p>
                  <p className="font-semibold mt-1 text-textPrimary">{citationModal.section_id}</p>
                </div>
              </div>

              <div className="bg-slate-950/30 border border-borderDark p-4 rounded-xl">
                <h4 className="text-[10px] font-bold uppercase tracking-wider text-textSecondary mb-2 font-sans">Grounded Passage Text</h4>
                <p className="text-xs text-textPrimary leading-relaxed font-mono whitespace-pre-wrap max-h-60 overflow-y-auto">
                  {citationModal.text || "Loading authoritative text span metadata..."}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Copilot;
