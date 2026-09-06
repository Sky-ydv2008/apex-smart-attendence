import React, { useState, useEffect } from 'react';
import { reportsAPI, classesAPI } from '../api';
import {
  BarChart3,
  FileSpreadsheet,
  FileText,
  Download,
  AlertTriangle,
  Users,
  CheckCircle2,
  Calendar,
  Filter
} from 'lucide-react';

export default function Reports() {
  const [summary, setSummary] = useState(null);
  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      reportsAPI.getSummary(),
      classesAPI.getAll()
    ]).then(([sumRes, clsRes]) => {
      setSummary(sumRes.data);
      setClasses(clsRes.data);
      setLoading(false);
    });
  }, []);

  const handleExport = (format) => {
    let url = '';
    if (format === 'csv') url = reportsAPI.getCSVUrl(selectedDate, selectedClassId);
    if (format === 'excel') url = reportsAPI.getExcelUrl(selectedDate, selectedClassId);
    if (format === 'pdf') url = reportsAPI.getPDFUrl(selectedDate, selectedClassId);

    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-indigo-400" />
            <span>Attendance Reports & Export Analytics Studio</span>
          </h2>
          <p className="text-xs text-slate-400">Generate executive summary reports and download PDF, Excel, or CSV files</p>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleExport('pdf')}
            className="px-3.5 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-rose-600/20 flex items-center space-x-1.5 transition-all"
          >
            <FileText className="w-4 h-4" />
            <span>Export PDF</span>
          </button>
          <button
            onClick={() => handleExport('excel')}
            className="px-3.5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-emerald-600/20 flex items-center space-x-1.5 transition-all"
          >
            <FileSpreadsheet className="w-4 h-4" />
            <span>Export Excel (.xlsx)</span>
          </button>
          <button
            onClick={() => handleExport('csv')}
            className="px-3.5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/20 flex items-center space-x-1.5 transition-all"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter Controls */}
      <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Filter by Date</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Filter by Class Section</label>
          <select
            value={selectedClassId}
            onChange={(e) => setSelectedClassId(e.target.value)}
            className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
          >
            <option value="">All Classes</option>
            {classes.map((c) => (
              <option key={c.id} value={c.id}>{c.name} ({c.section})</option>
            ))}
          </select>
        </div>
      </div>

      {/* Low Attendance Warning Alerts (<75%) */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
        <div className="flex items-center space-x-2 text-amber-400 font-bold text-base">
          <AlertTriangle className="w-5 h-5" />
          <h3>Low Attendance Student Risk Alerts (&lt;75% Attendance)</h3>
        </div>

        {summary?.low_attendance_alerts && summary.low_attendance_alerts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {summary.low_attendance_alerts.map((al, idx) => (
              <div key={idx} className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-between">
                <div>
                  <h4 className="font-bold text-white text-sm">{al.name}</h4>
                  <p className="text-xs text-slate-400">ID: <span className="text-amber-300 font-mono">{al.student_id}</span> | Class: {al.class_name}</p>
                </div>
                <div className="text-right">
                  <span className="px-2.5 py-1 rounded-full bg-amber-500 text-slate-950 font-extrabold text-xs">
                    {al.attendance_rate}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-sm flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <span>All students are maintaining healthy attendance rates above 75%!</span>
          </div>
        )}
      </div>
    </div>
  );
}
