import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import LiveScanner from './pages/LiveScanner';
import Sessions from './pages/Sessions';
import ClassesStudents from './pages/ClassesStudents';
import Records from './pages/Records';
import Reports from './pages/Reports';
import IDCardStudio from './pages/IDCardStudio';

function MainApp() {
  const { teacher, loading } = useAuth();
  const [activePage, setActivePage] = useState('dashboard');
  const [selectedSessionId, setSelectedSessionId] = useState(null);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-indigo-400 font-bold">
        <span>Initializing AttendAI Engine...</span>
      </div>
    );
  }

  if (!teacher) {
    return <Login />;
  }

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard setActivePage={setActivePage} setSelectedSessionId={setSelectedSessionId} />;
      case 'scanner':
        return <LiveScanner selectedSessionId={selectedSessionId} />;
      case 'sessions':
        return <Sessions setActivePage={setActivePage} setSelectedSessionId={setSelectedSessionId} />;
      case 'classes':
        return <ClassesStudents />;
      case 'records':
        return <Records />;
      case 'reports':
        return <Reports />;
      case 'cards':
        return <IDCardStudio />;
      default:
        return <Dashboard setActivePage={setActivePage} setSelectedSessionId={setSelectedSessionId} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased">
      <Navbar activePage={activePage} setActivePage={setActivePage} />
      <div className="flex flex-1">
        <Sidebar activePage={activePage} setActivePage={setActivePage} />
        <main className="flex-1 p-6 max-w-7xl mx-auto w-full">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
