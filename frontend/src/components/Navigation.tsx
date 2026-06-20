import React from 'react';
import { NavLink } from 'react-router-dom';
import { Bot, Activity, Ticket, BarChart2, Cpu, Landmark } from 'lucide-react';

interface NavigationProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

const Navigation: React.FC<NavigationProps> = ({ sidebarOpen, setSidebarOpen }) => {
  const navItems = [
    { to: '/', name: 'Telecom Copilot', icon: Bot },
    { to: '/network', name: 'Network Status', icon: Activity },
    { to: '/tickets', name: 'Ticket Management', icon: Ticket },
    { to: '/evaluation', name: 'Evaluation Dashboard', icon: BarChart2 },
    { to: '/architecture', name: 'System Architecture', icon: Cpu },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/60 md:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <aside 
        className={`fixed md:sticky top-0 left-0 z-40 w-64 h-screen border-r border-borderDark glass-panel transition-transform duration-300 flex flex-col justify-between ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="flex-1 overflow-y-auto px-4 py-6">
          {/* Header */}
          <div className="flex items-center gap-3 px-2 mb-8">
            <div className="p-2 bg-primary/10 rounded-lg border border-primary/20">
              <Landmark className="h-6 w-6 text-primary" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-textPrimary leading-none">TelecomRAG</h1>
              <span className="text-xs text-primary/80 font-medium font-mono uppercase tracking-wider">Copilot Ops</span>
            </div>
          </div>

          {/* Links */}
          <nav className="space-y-1.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all group ${
                      isActive
                        ? 'bg-primary/10 text-primary border border-primary/20 shadow-[0_0_15px_rgba(0,229,255,0.15)]'
                        : 'text-textSecondary hover:bg-white/5 hover:text-textPrimary border border-transparent'
                    }`
                  }
                >
                  <Icon className="h-5 w-5 transition-transform group-hover:scale-105" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-borderDark bg-surface/30">
          <div className="flex items-center gap-3 px-2">
            <div className="h-2 w-2 rounded-full bg-success animate-ping" />
            <div className="text-xs text-textSecondary">
              System Status: <span className="text-success font-semibold">Online</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Navigation;
