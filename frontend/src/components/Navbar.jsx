import React from 'react';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Cpu, LogOut, User, WifiOff, Bell } from 'lucide-react';

export default function Navbar({ activePage, setActivePage }) {
  const { teacher, logout } = useAuth();

  return (
    <header className="bg-slate-900/90 backdrop-blur border-b border-slate-800 sticky top-0 z-40 px-6 py-3.5">
      <div className="flex items-center justify-between">
        {/* Brand & Offline Status Badge */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2.5 cursor-pointer" onClick={() => setActivePage('dashboard')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-indigo-200">
                AttendAI
              </h1>
              <p className="text-xs text-indigo-400 font-medium">Smart Attendance Platform</p>
            </div>
          </div>

          {/* 100% Offline Zero-WiFi Indicator Badge */}
          <div className="hidden sm:flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <WifiOff className="w-3.5 h-3.5" />
            <span>100% Local / Zero Cloud AI</span>
          </div>
        </div>

        {/* Right Action Icons & User Info */}
        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60 text-xs text-slate-300">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span>AI Models: <strong className="text-white">OCR + Face Embeddings</strong></span>
          </div>

          {teacher && (
            <div className="flex items-center space-x-3 border-l border-slate-800 pl-4">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 flex items-center justify-center font-bold text-sm">
                  {teacher.name.charAt(0)}
                </div>
                <div className="hidden lg:block text-left">
                  <p className="text-sm font-semibold text-slate-200 leading-none">{teacher.name}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{teacher.department}</p>
                </div>
              </div>

              <button
                onClick={logout}
                title="Logout"
                className="p-2 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
