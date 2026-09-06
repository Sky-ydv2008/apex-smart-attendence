import React, { useState, useEffect } from 'react';
import { sessionsAPI, classesAPI } from '../api';
import {
  Clock,
  Plus,
  Play,
  Square,
  Camera,
  CheckCircle2,
  AlertCircle,
  X,
  Users
} from 'lucide-react';

export default function Sessions({ setActivePage, setSelectedSessionId }) {
  const [sessions, setSessions] = useState([]);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Create Session Form State
  const [classId, setClassId] = useState('');
  const [subjectId, setSubjectId] = useState('1'); // Default Data Structures
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('10:00');
  const [lateThreshold, setLateThreshold] = useState('10');

  const fetchSessionsData = async () => {
    try {
      const [sessRes, clsRes] = await Promise.all([
        sessionsAPI.getAll(),
        classesAPI.getAll()
      ]);
      setSessions(sessRes.data);
      setClasses(clsRes.data);
      if (!classId && clsRes.data.length > 0) {
        setClassId(clsRes.data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessionsData();
  }, []);

  const handleCreateSession = async (e) => {
    e.preventDefault();
    try {
      await sessionsAPI.create({
        class_id: Number(classId),
        subject_id: Number(subjectId),
        date,
        start_time: startTime,
        end_time: endTime,
        late_threshold_minutes: Number(lateThreshold),
        verification_mode: 'ocr_face'
      });
      setShowCreateModal(false);
      fetchSessionsData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create attendance session');
    }
  };

  const handleStartSession = async (id) => {
    try {
      await sessionsAPI.start(id);
      fetchSessionsData();
    } catch (err) {
      alert('Failed to start session');
    }
  };

  const handleStopSession = async (id) => {
    if (!confirm('Close session? Any enrolled student who has not scanned in will automatically be marked ABSENT.')) return;
    try {
      const res = await sessionsAPI.stop(id);
      alert(res.data.message);
      fetchSessionsData();
    } catch (err) {
      alert('Failed to close session');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Clock className="w-5 h-5 text-indigo-400" />
            <span>Classroom Attendance Sessions Studio</span>
          </h2>
          <p className="text-xs text-slate-400">Configure time windows, late thresholds, and session status</p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 flex items-center space-x-1.5 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>New Attendance Session</span>
        </button>
      </div>

      {/* Sessions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sessions.map((s) => (
          <div key={s.id} className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 shadow-lg hover:border-slate-700 transition-all flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-indigo-400">SESSION #{s.id}</span>
                <span className={`px-2.5 py-1 rounded-full text-xs font-extrabold uppercase ${
                  s.status === 'active' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                  s.status === 'closed' ? 'bg-slate-800 text-slate-400 border border-slate-700' :
                  'bg-indigo-500/20 text-indigo-300'
                }`}>
                  {s.status}
                </span>
              </div>

              <h3 className="text-lg font-bold text-white">
                {s.class_name} — {s.subject_name} ({s.subject_code})
              </h3>
              <p className="text-xs text-slate-400">
                Date: <strong className="text-slate-200">{s.date}</strong> | Time Window: <strong className="text-slate-200">{s.start_time} - {s.end_time}</strong> (Late &gt; {s.late_threshold_minutes}m)
              </p>
            </div>

            {/* Attendance Progress Stats */}
            <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80 grid grid-cols-3 gap-2 text-center text-xs">
              <div>
                <span className="text-slate-500 block text-[10px] font-bold uppercase">Present</span>
                <strong className="text-emerald-400 text-sm">{s.present_count}</strong>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] font-bold uppercase">Late</span>
                <strong className="text-amber-400 text-sm">{s.late_count}</strong>
              </div>
              <div>
                <span className="text-slate-500 block text-[10px] font-bold uppercase">Absent</span>
                <strong className="text-rose-400 text-sm">{s.absent_count}</strong>
              </div>
            </div>

            {/* Action Bar */}
            <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
              <span className="text-xs text-slate-400 font-medium">
                Enrolled: {s.total_students} | Rate: <strong className="text-white">{s.attendance_rate}%</strong>
              </span>

              <div className="flex items-center space-x-2">
                {s.status === 'active' ? (
                  <>
                    <button
                      onClick={() => {
                        if (setSelectedSessionId) setSelectedSessionId(s.id);
                        setActivePage('scanner');
                      }}
                      className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl flex items-center space-x-1 shadow-md shadow-indigo-600/30"
                    >
                      <Camera className="w-3.5 h-3.5" />
                      <span>Scan Feed</span>
                    </button>
                    <button
                      onClick={() => handleStopSession(s.id)}
                      className="px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-semibold rounded-xl border border-rose-500/30 flex items-center space-x-1"
                    >
                      <Square className="w-3.5 h-3.5" />
                      <span>Close Session</span>
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => handleStartSession(s.id)}
                    className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-xl flex items-center space-x-1"
                  >
                    <Play className="w-3.5 h-3.5" />
                    <span>Start Session</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal: Create Session */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">Create Attendance Session</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleCreateSession} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Class</label>
                <select
                  value={classId}
                  onChange={(e) => setClassId(e.target.value)}
                  className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                >
                  {classes.map((c) => (
                    <option key={c.id} value={c.id}>{c.name} ({c.section})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Subject</label>
                <select
                  value={subjectId}
                  onChange={(e) => setSubjectId(e.target.value)}
                  className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                >
                  <option value="1">CS201 — Data Structures & Algorithms</option>
                  <option value="2">CS302 — AI & Machine Learning</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Date</label>
                  <input
                    type="date"
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Late Threshold (Mins)</label>
                  <input
                    type="number"
                    value={lateThreshold}
                    onChange={(e) => setLateThreshold(e.target.value)}
                    className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Start Time</label>
                  <input
                    type="time"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">End Time</label>
                  <input
                    type="time"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                  />
                </div>
              </div>

              <button type="submit" className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-sm">
                Create & Activate Attendance Session
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
