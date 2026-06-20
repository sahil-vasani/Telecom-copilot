import React from 'react';
import { Menu, Cpu, Bell, Activity } from 'lucide-react';

interface TopbarProps {
  setSidebarOpen: (open: boolean) => void;
}

const Topbar: React.FC<TopbarProps> = ({ setSidebarOpen }) => {
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between px-6 py-4 border-b border-borderDark glass-panel bg-background/80 backdrop-blur-md">
      {/* Mobile toggle */}
      <div className="flex items-center gap-4">
        <button 
          onClick={() => setSidebarOpen(true)}
          className="p-1.5 text-textSecondary hover:text-textPrimary md:hidden hover:bg-white/5 rounded-lg"
        >
          <Menu className="h-6 w-6" />
        </button>
        <div className="hidden md:flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-textSecondary">
          <Cpu className="h-4 w-4 text-primary" />
          <span>Operational Dashboard</span>
        </div>
      </div>

      {/* Telemetry Actions */}
      <div className="flex items-center gap-4">
        {/* Diagnostic status */}
        <div className="hidden sm:flex items-center gap-4 px-3 py-1.5 bg-slate-900/60 rounded-full border border-borderDark text-xs font-medium text-textSecondary">
          <div className="flex items-center gap-1.5">
            <Activity className="h-3.5 w-3.5 text-success" />
            <span>Dense Retrieval: <span className="text-textPrimary">BGE-1.5</span></span>
          </div>
          <div className="h-3 w-[1px] bg-borderDark" />
          <div className="flex items-center gap-1.5">
            <span>Reranker: <span className="text-primary font-mono">MiniLM-L6</span></span>
          </div>
        </div>

        {/* Notifications */}
        <button className="relative p-1.5 text-textSecondary hover:text-textPrimary hover:bg-white/5 rounded-lg">
          <Bell className="h-5 w-5" />
          <span className="absolute top-1 right-1 h-2 w-2 bg-primary rounded-full animate-pulse-slow" />
        </button>

        {/* Profile Avatar */}
        <div className="flex items-center gap-3 pl-2 border-l border-borderDark">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-primary to-emerald-400 p-[1px]">
            <div className="h-full w-full bg-surface rounded-lg flex items-center justify-center font-bold text-xs text-primary">
              OP
            </div>
          </div>
          <div className="hidden lg:block text-left">
            <p className="text-xs font-semibold text-textPrimary leading-none">Ops Center</p>
            <span className="text-[10px] text-textSecondary font-medium">Administrator</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Topbar;
