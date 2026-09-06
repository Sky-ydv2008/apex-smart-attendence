import React, { useState, useEffect } from 'react';
import { attendanceAPI, sessionsAPI } from '../api';
import {
  FileCheck,
  Search,
  Edit,
  ShieldCheck,
  CheckCircle2,
  Clock,
  XCircle,
  X,
  AlertTriangle
} from 'lucide-react';

export default function Records() {
  const [sessions, setSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState('');
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  // Override Modal
  const [overrideRecord, setOverrideRecord] = useState(null);
  const [newStatus, setNewStatus] = useState('present');
  const [overrideReason, setOverrideReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchRecords = async () => {
    try {
      const sessRes = await sessionsAPI.getAll();
      setSessions(sessRes.data);
      if (sessRes.data.length > 0) {
        const activeId = selectedSessionId || sessRes.data[0].id;
        setSelectedSessionId(activeId);
        const recRes = await attendanceAPI.getBySession(activeId);
        setRecords(recRes.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [selectedSessionId]);

  const handleOverrideSubmit = async (e) => {
    e.preventDefault();
    if (!overrideReason.trim()) {
      alert('Please enter a valid reason for manual teacher override.');
      return;
    }

    setSubmitting(true);
    try {
      await attendanceAPI.override({
        record_id: overrideRecord.id,
        new_status: newStatus,
        reason: overrideReason
      });
      setOverrideRecord(null);
      setOverrideReason('');
      fetchRecords();
    } catch (err) {
      alert(err.response?.data?.detail || 'Override failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <FileCheck className="w-5 h-5 text-indigo-400" />
            <span>Attendance Records & Teacher Audit Override Studio</span>
          </h2>
          <p className="text-xs text-slate-400">View detailed verification confidence and perform audit logged status corrections</p>
        </div>

        <select
          value={selectedSessionId}
          onChange={(e) => setSelectedSessionId(e.target.value)}
          className="px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm font-semibold text-white focus:outline-none focus:border-indigo-500"
        >
          {sessions.map((s) => (
            <option key={s.id} value={s.id}>
              Session #{s.id}: {s.class_name} — {s.subject_code} ({s.date})
            </option>
          ))}
        </select>
      </div>

      {/* Attendance Records Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 font-bold uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-4">Student</th>
                <th className="p-4">ID Code</th>
                <th className="p-4">Timestamp</th>
                <th className="p-4">Status</th>
                <th className="p-4">Verification Method</th>
                <th className="p-4">Face Conf</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {records.length > 0 ? (
                records.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-4 font-bold text-white text-sm">
                      {r.student_name}
                      <span className="block text-xs font-normal text-slate-400">Roll: {r.roll_number}</span>
                    </td>
                    <td className="p-4 font-mono text-indigo-300 font-semibold">{r.student_code}</td>
                    <td className="p-4 text-slate-400">
                      {new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 rounded-md text-[11px] font-extrabold uppercase ${
                        r.status === 'present' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                        r.status === 'late' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                        'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                      }`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="p-4 text-slate-400">
                      <span className="capitalize">{r.verification_method.replace('_', ' ')}</span>
                      {r.override_reason && (
                        <span className="block text-[10px] text-amber-300 mt-0.5 truncate max-w-xs" title={r.override_reason}>
                          Note: {r.override_reason}
                        </span>
                      )}
                    </td>
                    <td className="p-4 font-mono font-semibold text-purple-400">
                      {(r.face_confidence * 100).toFixed(1)}%
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => {
                          setOverrideRecord(r);
                          setNewStatus(r.status);
                        }}
                        className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-lg border border-slate-700 flex items-center space-x-1 ml-auto"
                      >
                        <Edit className="w-3.5 h-3.5" />
                        <span>Override</span>
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="p-8 text-center text-slate-500">
                    No attendance records found for this session.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal: Teacher Override */}
      {overrideRecord && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-lg font-bold text-white">Manual Teacher Override</h3>
                <p className="text-xs text-slate-400">Student: {overrideRecord.student_name} ({overrideRecord.student_code})</p>
              </div>
              <button onClick={() => setOverrideRecord(null)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleOverrideSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">New Attendance Status</label>
                <select
                  value={newStatus}
                  onChange={(e) => setNewStatus(e.target.value)}
                  className="w-full p-3 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm font-bold uppercase"
                >
                  <option value="present">PRESENT</option>
                  <option value="late">LATE</option>
                  <option value="absent">ABSENT</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Mandatory Audit Reason</label>
                <textarea
                  required
                  rows="3"
                  placeholder="e.g. Card unreadable due to glare; student identity verified manually by teacher."
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  className="w-full p-3 bg-slate-800 border border-slate-700 rounded-xl text-white text-xs placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                ></textarea>
              </div>

              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>This change will be permanently logged in SQLite audit records with your teacher signature.</span>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-sm disabled:opacity-50"
              >
                {submitting ? 'Saving Override...' : 'Confirm Audit Logged Override'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
