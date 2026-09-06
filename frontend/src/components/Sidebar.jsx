import React from 'react';
import {
  LayoutDashboard,
  Users,
  Clock,
  Camera,
  FileCheck,
  BarChart3,
  CreditCard,
  Settings
} from 'lucide-react';

export default function Sidebar({ activePage, setActivePage }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'scanner', label: 'Live AI Scanner', icon: Camera, highlight: true },
    { id: 'sessions', label: 'Attendance Sessions', icon: Clock },
    { id: 'classes', label: 'Classes & Students', icon: Users },
    { id: 'records', label: 'Records & Overrides', icon: FileCheck },
    { id: 'reports', label: 'Reports & Export', icon: BarChart3 },
    { id: 'cards', label: 'ID Cards Studio', icon: CreditCard },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 min-h-[calc(100vh-65px)]">
      <div className="p-4 space-y-1.5 flex-1">
        <p className="px-3 text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Main Menu</p>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-150 ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/25 font-semibold'
                  : item.highlight
                  ? 'bg-indigo-500/10 text-indigo-300 hover:bg-indigo-500/20 border border-indigo-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : item.highlight ? 'text-indigo-400' : 'text-slate-400'}`} />
              <span>{item.label}</span>
              {item.highlight && !isActive && (
                <span className="ml-auto text-[10px] uppercase tracking-wider font-extrabold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
                  LIVE
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer Info Box */}
      <div className="p-4 m-3 rounded-xl bg-slate-800/50 border border-slate-800 text-xs text-slate-400">
        <div className="flex items-center space-x-2 font-semibold text-slate-300 mb-1">
          <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
          <span>AttendAI Offline v1.0</span>
        </div>
        <p className="text-[11px] text-slate-500">Hardware-accelerated OpenCV & Local Embeddings.</p>
      </div>
    </aside>
  );
}
