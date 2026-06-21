import React, { useState } from 'react';
import Navigation from '../components/Navigation';
import Topbar from '../components/Topbar';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-background text-textPrimary">
      {/* Sidebar Navigation */}
      <Navigation sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />

      {/* Main content grid */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Top Navbar */}
        <Topbar setSidebarOpen={setSidebarOpen} />

        {/* Dynamic Route Screen */}
        <main className="flex-1 overflow-y-auto px-6 py-6 md:px-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default MainLayout;
