import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getTickets } from '../services/api';
import { Ticket } from '../types';
import { 
  Search, ShieldAlert, CheckCircle2, Clock, X, ChevronRight, 
  Info, ExternalLink, Calendar, Phone, AlertCircle
} from 'lucide-react';
import { cn } from '../utils/helpers';

const Tickets: React.FC = () => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'open' | 'in_progress' | 'closed'>('all');
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const data = await getTickets();
        setTickets(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const getSeverityColor = (severity: Ticket['severity']) => {
    switch (severity) {
      case 'low': return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
      case 'medium': return 'bg-warning/10 text-warning border-warning/20';
      case 'high': return 'bg-orange-500/10 text-orange-500 border-orange-500/20';
      case 'critical': return 'bg-error/10 text-error border-error/20';
    }
  };

  const getStatusColor = (status: Ticket['status']) => {
    switch (status) {
      case 'open': return 'bg-primary/10 text-primary border-primary/20';
      case 'in_progress': return 'bg-orange-500/10 text-orange-500 border-orange-500/20';
      case 'closed': return 'bg-success/10 text-success border-success/20';
    }
  };

  const filteredTickets = tickets.filter(ticket => {
    const matchesSearch = 
      ticket.ticket_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.category.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || ticket.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6 relative h-[calc(100vh-100px)] overflow-hidden">
      {/* Top action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="text-left">
          <h1 className="text-xl font-bold text-textPrimary leading-none">Ticket Management</h1>
          <p className="text-xs text-textSecondary mt-1">Review, assign, and track RAG-escalated customer complaints.</p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-4.5 w-4.5 text-textSecondary" />
          <input
            type="text"
            placeholder="Search tickets, IDs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-slate-900 border border-borderDark focus:border-primary text-xs rounded-xl text-textPrimary outline-none transition-all"
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-borderDark pb-[1px] gap-2">
        {(['all', 'open', 'in_progress', 'closed'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setStatusFilter(status)}
            className={cn(
              "px-4 py-2.5 text-xs font-semibold capitalize border-b-2 -mb-[2px] transition-all",
              statusFilter === status 
                ? "border-primary text-primary" 
                : "border-transparent text-textSecondary hover:text-textPrimary"
            )}
          >
            {status.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Main content window */}
      <div className="h-[calc(100%-120px)] overflow-y-auto pr-1">
        {loading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="glass-panel h-16 rounded-xl animate-pulse" />
            ))}
          </div>
        ) : filteredTickets.length > 0 ? (
          <div className="space-y-3">
            {filteredTickets.map((ticket) => (
              <div
                key={ticket.ticket_id}
                onClick={() => setSelectedTicket(ticket)}
                className="glass-panel hover:border-slate-800 p-4 rounded-xl flex items-center justify-between gap-6 cursor-pointer group transition-all text-left"
              >
                <div className="flex items-center gap-4 truncate">
                  {/* Category icon indicator */}
                  <div className="p-2.5 bg-slate-950/40 border border-borderDark rounded-lg shrink-0">
                    <ShieldAlert className="h-5 w-5 text-textSecondary group-hover:text-primary transition-colors" />
                  </div>
                  
                  <div className="truncate">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-textPrimary">{ticket.ticket_id}</span>
                      <span className="px-2 py-0.5 rounded text-[8px] font-bold font-sans uppercase bg-slate-950/40 text-textSecondary border border-borderDark">
                        {ticket.category}
                      </span>
                    </div>
                    <p className="text-xs text-textSecondary truncate mt-1 max-w-lg">{ticket.summary}</p>
                  </div>
                </div>

                {/* Status and telemetry options */}
                <div className="flex items-center gap-4 shrink-0 font-mono text-xs">
                  <span className={cn(
                    "px-2.5 py-0.5 rounded-full border text-[9px] font-bold uppercase",
                    getSeverityColor(ticket.severity)
                  )}>
                    {ticket.severity}
                  </span>
                  
                  <span className={cn(
                    "px-2.5 py-0.5 rounded-full border text-[9px] font-bold uppercase",
                    getStatusColor(ticket.status)
                  )}>
                    {ticket.status.replace('_', ' ')}
                  </span>
                  
                  <ChevronRight className="h-5 w-5 text-textSecondary group-hover:text-textPrimary transition-colors" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="glass-panel p-12 rounded-xl text-center text-xs text-textSecondary flex flex-col items-center justify-center gap-3">
            <AlertCircle className="h-8 w-8 text-textSecondary/40" />
            <p>No tickets matches search criteria.</p>
          </div>
        )}
      </div>

      {/* DETAIL TICKET SLIDING SIDE DRAWER */}
      <AnimatePresence>
        {selectedTicket && (
          <>
            {/* Overlay backdrop */}
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedTicket(null)}
              className="fixed inset-0 z-40 bg-black/60 backdrop-blur-xs"
            />
            {/* Panel */}
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 220 }}
              className="fixed top-0 right-0 z-50 w-full sm:w-[480px] h-screen border-l border-borderDark glass-panel bg-background flex flex-col justify-between"
            >
              <div>
                {/* Header */}
                <div className="p-6 border-b border-borderDark flex items-center justify-between bg-surface/50">
                  <div className="text-left">
                    <span className="text-[10px] text-primary uppercase font-mono font-bold">Ticket Details</span>
                    <h2 className="text-base font-bold text-textPrimary font-mono mt-0.5">{selectedTicket.ticket_id}</h2>
                  </div>
                  <button 
                    onClick={() => setSelectedTicket(null)}
                    className="p-1 text-textSecondary hover:text-textPrimary hover:bg-white/5 rounded-lg border border-borderDark"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                {/* Body Details */}
                <div className="p-6 space-y-6 text-left overflow-y-auto h-[calc(100vh-160px)]">
                  {/* Status telemetry block */}
                  <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                    <div className="bg-slate-950/45 p-3 rounded-xl border border-borderDark">
                      <p className="text-[10px] text-textSecondary">SLA Resolution ETA</p>
                      <p className="font-semibold text-textPrimary mt-1 flex items-center gap-1.5">
                        <Clock className="h-4 w-4 text-primary" />
                        {selectedTicket.eta_hours} Hours
                      </p>
                    </div>
                    <div className="bg-slate-950/45 p-3 rounded-xl border border-borderDark">
                      <p className="text-[10px] text-textSecondary">Creation Stamp</p>
                      <p className="font-semibold text-textPrimary mt-1 flex items-center gap-1.5">
                        <Calendar className="h-4 w-4 text-emerald-400" />
                        {new Date(selectedTicket.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {/* Summary card */}
                  <div className="bg-slate-950/20 border border-borderDark p-4 rounded-xl">
                    <h4 className="text-[10px] font-bold uppercase tracking-wider text-textSecondary mb-2">Escalation Summary</h4>
                    <p className="text-xs text-textPrimary leading-relaxed leading-normal">
                      {selectedTicket.summary}
                    </p>
                  </div>

                  {/* Settings status */}
                  <div className="space-y-4">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-textSecondary border-b border-white/5 pb-1">Telemetry States</h4>
                    
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-textSecondary">Category Queue</span>
                      <span className="text-textPrimary font-semibold capitalize">{selectedTicket.category}</span>
                    </div>

                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-textSecondary">Ticket Severity</span>
                      <span className={cn(
                        "px-2.5 py-0.5 rounded-full border text-[10px] font-bold uppercase",
                        getSeverityColor(selectedTicket.severity)
                      )}>
                        {selectedTicket.severity}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-textSecondary">Active Status</span>
                      <span className={cn(
                        "px-2.5 py-0.5 rounded-full border text-[10px] font-bold uppercase",
                        getStatusColor(selectedTicket.status)
                      )}>
                        {selectedTicket.status.replace('_', ' ')}
                      </span>
                    </div>

                    {selectedTicket.customer_mobile && (
                      <div className="flex items-center justify-between text-xs font-mono">
                        <span className="text-textSecondary">Customer Mobile</span>
                        <span className="text-textPrimary font-semibold flex items-center gap-1">
                          <Phone className="h-3.5 w-3.5 text-primary" />
                          {selectedTicket.customer_mobile}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Drawer Footer Actions */}
              <div className="p-4 border-t border-borderDark bg-surface/50 flex items-center gap-2">
                <a 
                  href={selectedTicket.reference_url || "#"} 
                  target="_blank" 
                  rel="noreferrer"
                  className="flex-1 flex items-center justify-center gap-2 py-2.5 bg-primary text-background hover:bg-primary/95 text-xs font-bold rounded-xl transition-all shadow-[0_0_15px_rgba(0,229,255,0.15)]"
                >
                  <ExternalLink className="h-4 w-4" />
                  <span>Open in CRM Portal</span>
                </a>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default Tickets;
