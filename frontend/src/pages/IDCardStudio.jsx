import React, { useState, useEffect } from 'react';
import { studentsAPI, classesAPI } from '../api';
import { CreditCard, Download, Printer, Search, User } from 'lucide-react';

export default function IDCardStudio() {
  const [students, setStudents] = useState([]);
  const [classes, setClasses] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState('');
  const [search, setSearch] = useState('');

  const fetchStudents = async () => {
    try {
      const [stuRes, clsRes] = await Promise.all([
        studentsAPI.getAll({ class_id: selectedClassId || undefined, search: search || undefined }),
        classesAPI.getAll()
      ]);
      setStudents(stuRes.data);
      setClasses(clsRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [selectedClassId, search]);

  const handlePrintAll = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <CreditCard className="w-5 h-5 text-indigo-400" />
            <span>Student ID Cards & QR Printable Studio</span>
          </h2>
          <p className="text-xs text-slate-400">Official student identity cards with scannable QR and photo credentials</p>
        </div>

        <button
          onClick={handlePrintAll}
          className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 flex items-center space-x-1.5 transition-all"
        >
          <Printer className="w-4 h-4" />
          <span>Print All ID Cards</span>
        </button>
      </div>

      {/* Filter */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <input
          type="text"
          placeholder="Search student..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="p-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500"
        />
        <select
          value={selectedClassId}
          onChange={(e) => setSelectedClassId(e.target.value)}
          className="p-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white"
        >
          <option value="">All Classes</option>
          {classes.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {/* ID Cards Gallery */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 print:grid-cols-2">
        {students.map((st) => (
          <div key={st.id} className="p-4 rounded-2xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="bg-slate-950 p-2 rounded-xl border border-slate-800 flex justify-center">
              <img
                src={`/uploads/cards/card_${st.student_id}.png`}
                alt={`ID Card ${st.name}`}
                className="rounded-lg max-w-full shadow-lg"
              />
            </div>
            <div className="flex items-center justify-between text-xs px-1">
              <div>
                <strong className="text-white block">{st.name}</strong>
                <span className="text-indigo-400 font-mono">{st.student_id}</span>
              </div>
              <a
                href={`/uploads/cards/card_${st.student_id}.png`}
                download={`card_${st.student_id}.png`}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-lg flex items-center space-x-1"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Save</span>
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
