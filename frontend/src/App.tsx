import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Copilot from './pages/Copilot';
import Network from './pages/Network';
import Tickets from './pages/Tickets';
import Evaluation from './pages/Evaluation';
import Architecture from './pages/Architecture';

const App: React.FC = () => {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Copilot />} />
          <Route path="/network" element={<Network />} />
          <Route path="/tickets" element={<Tickets />} />
          <Route path="/evaluation" element={<Evaluation />} />
          <Route path="/architecture" element={<Architecture />} />
        </Routes>
      </MainLayout>
    </Router>
  );
};

export default App;
