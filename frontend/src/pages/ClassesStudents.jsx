import React, { useState, useEffect } from 'react';
import { classesAPI, studentsAPI } from '../api';
import {
  Users,
  Plus,
  Search,
  Upload,
  CreditCard,
  Trash2,
  CheckCircle2,
  AlertCircle,
  X,
  Camera
} from 'lucide-react';

export default function ClassesStudents() {
  const [classes, setClasses] = useState([]);
  const [students, setStudents] = useState([]);
  const [selectedClassId, setSelectedClassId] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  // Modals
  const [showAddClass, setShowAddClass] = useState(false);
  const [showAddStudent, setShowAddStudent] = useState(false);
  const [enrollStudent, setEnrollStudent] = useState(null); // student object for face photo upload modal
  const [viewCardStudent, setViewCardStudent] = useState(null); // student object for ID Card preview

  // Forms
  const [newClassName, setNewClassName] = useState('');
  const [newClassSection, setNewClassSection] = useState('A');
  
  const [newStudentId, setNewStudentId] = useState('');
  const [newStudentName, setNewStudentName] = useState('');
  const [newStudentRoll, setNewStudentRoll] = useState('');
  const [newStudentClassId, setNewStudentClassId] = useState('');

  const [faceFile, setFaceFile] = useState(null);
  const [enrolling, setEnrolling] = useState(false);

  const fetchData = async () => {
    try {
      const [clsRes, stuRes] = await Promise.all([
        classesAPI.getAll(),
        studentsAPI.getAll({ class_id: selectedClassId || undefined, search: searchQuery || undefined })
      ]);
      setClasses(clsRes.data);
      setStudents(stuRes.data);
      if (!newStudentClassId && clsRes.data.length > 0) {
        setNewStudentClassId(clsRes.data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedClassId, searchQuery]);

  const handleCreateClass = async (e) => {
    e.preventDefault();
    try {
      await classesAPI.create({ name: newClassName, section: newClassSection });
      setNewClassName('');
      setShowAddClass(false);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create class');
    }
  };

  const handleCreateStudent = async (e) => {
    e.preventDefault();
    try {
      await studentsAPI.create({
        student_id: newStudentId,
        name: newStudentName,
        roll_number: newStudentRoll,
        class_id: Number(newStudentClassId)
      });
      setNewStudentId('');
      setNewStudentName('');
      setNewStudentRoll('');
      setShowAddStudent(false);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to create student');
    }
  };

  const handleFaceEnrollmentSubmit = async (e) => {
    e.preventDefault();
    if (!faceFile || !enrollStudent) return;

    setEnrolling(true);
    const formData = new FormData();
    formData.append('file', faceFile);

    try {
      await studentsAPI.enrollFace(enrollStudent.id, formData);
      alert(`Face successfully enrolled for ${enrollStudent.name}!`);
      setEnrollStudent(null);
      setFaceFile(null);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Face enrollment failed. Make sure a clear face is visible.');
    } finally {
      setEnrolling(false);
    }
  };

  const handleDeleteStudent = async (id, name) => {
    if (!confirm(`Are you sure you want to delete student ${name}?`)) return;
    try {
      await studentsAPI.delete(id);
      fetchData();
    } catch (err) {
      alert('Failed to delete student');
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Action Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Users className="w-5 h-5 text-indigo-400" />
            <span>Classroom & Student Enrollment Studio</span>
          </h2>
          <p className="text-xs text-slate-400">Manage student directories and local biometric face embeddings</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowAddClass(true)}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs rounded-xl border border-slate-700 flex items-center space-x-1.5 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Add Class</span>
          </button>
          <button
            onClick={() => setShowAddStudent(true)}
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-indigo-600/30 flex items-center space-x-1.5 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Enroll Student</span>
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="relative col-span-2">
          <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search by student name, ID code, or roll number..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <select
          value={selectedClassId}
          onChange={(e) => setSelectedClassId(e.target.value)}
          className="px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-sm text-slate-200 font-medium focus:outline-none focus:border-indigo-500"
        >
          <option value="">All Classes & Sections ({students.length} Students)</option>
          {classes.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name} ({c.section}) — {c.student_count} Enrolled
            </option>
          ))}
        </select>
      </div>

      {/* Students Directory Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {students.map((st) => (
          <div key={st.id} className="p-5 rounded-2xl bg-slate-900 border border-slate-800 space-y-4 hover:border-slate-700 transition-all flex flex-col justify-between">
            <div className="flex items-start space-x-4">
              <div className="w-14 h-14 rounded-xl bg-slate-800 border border-indigo-500/30 overflow-hidden shrink-0 flex items-center justify-center">
                {st.photo_url ? (
                  <img src={st.photo_url} alt={st.name} className="w-full h-full object-cover" />
                ) : (
                  <User className="w-7 h-7 text-slate-500" />
                )}
              </div>

              <div className="space-y-1 flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-white text-base truncate">{st.name}</h3>
                  <button
                    onClick={() => handleDeleteStudent(st.id, st.name)}
                    className="text-slate-500 hover:text-rose-400 p-1"
                    title="Delete Student"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-xs text-indigo-400 font-mono font-semibold">{st.student_id}</p>
                <p className="text-xs text-slate-400">Class: <strong className="text-slate-200">{st.class_name}</strong> | Roll: {st.roll_number}</p>
              </div>
            </div>

            {/* Face Status Badge & Action Controls */}
            <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className={`inline-flex items-center space-x-1 font-semibold ${
                st.has_face_enrolled ? 'text-emerald-400' : 'text-amber-400'
              }`}>
                {st.has_face_enrolled ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Face Enrolled</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                    <span>Needs Photo</span>
                  </>
                )}
              </span>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setEnrollStudent(st)}
                  className="px-2.5 py-1 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 rounded-lg border border-indigo-500/30 font-medium flex items-center space-x-1"
                >
                  <Camera className="w-3.5 h-3.5" />
                  <span>Face Photo</span>
                </button>

                <button
                  onClick={() => setViewCardStudent(st)}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg font-medium flex items-center space-x-1"
                >
                  <CreditCard className="w-3.5 h-3.5" />
                  <span>ID Card</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal: Add Class */}
      {showAddClass && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">Add New Classroom</h3>
              <button onClick={() => setShowAddClass(false)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleCreateClass} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Class Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. CSE-A"
                  value={newClassName}
                  onChange={(e) => setNewClassName(e.target.value)}
                  className="w-full p-3 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Section</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. A"
                  value={newClassSection}
                  onChange={(e) => setNewClassSection(e.target.value)}
                  className="w-full p-3 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                />
              </div>
              <button type="submit" className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-sm">
                Create Class
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Enroll Student */}
      {showAddStudent && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">Enroll New Student</h3>
              <button onClick={() => setShowAddStudent(false)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleCreateStudent} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Student ID Code</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. CS20260148"
                  value={newStudentId}
                  onChange={(e) => setNewStudentId(e.target.value)}
                  className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Rohan Verma"
                  value={newStudentName}
                  onChange={(e) => setNewStudentName(e.target.value)}
                  className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Roll Number</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 48"
                    value={newStudentRoll}
                    onChange={(e) => setNewStudentRoll(e.target.value)}
                    className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Class</label>
                  <select
                    value={newStudentClassId}
                    onChange={(e) => setNewStudentClassId(e.target.value)}
                    className="w-full p-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white text-sm"
                  >
                    {classes.map((c) => (
                      <option key={c.id} value={c.id}>{c.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <button type="submit" className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-sm">
                Save & Generate Student ID Card
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Enroll Face Photo */}
      {enrollStudent && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-lg font-bold text-white">Enroll Face Vector</h3>
                <p className="text-xs text-slate-400">Student: {enrollStudent.name} ({enrollStudent.student_id})</p>
              </div>
              <button onClick={() => setEnrollStudent(null)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleFaceEnrollmentSubmit} className="space-y-4">
              <div className="p-6 border-2 border-dashed border-slate-700 rounded-xl text-center space-y-2 bg-slate-800/40">
                <Upload className="w-8 h-8 text-indigo-400 mx-auto" />
                <p className="text-xs text-slate-300 font-semibold">Upload clear passport/face photo</p>
                <input
                  type="file"
                  accept="image/*"
                  required
                  onChange={(e) => setFaceFile(e.target.files[0])}
                  className="text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-500 cursor-pointer"
                />
              </div>

              <button
                type="submit"
                disabled={enrolling || !faceFile}
                className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl text-sm disabled:opacity-50"
              >
                {enrolling ? 'Extracting Local 128-Dim Vector...' : 'Generate & Save Face Embedding'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Modal: View ID Card */}
      {viewCardStudent && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-lg font-bold text-white">Student ID Card Preview</h3>
                <p className="text-xs text-slate-400">{viewCardStudent.name} — {viewCardStudent.student_id}</p>
              </div>
              <button onClick={() => setViewCardStudent(null)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <div className="bg-slate-950 p-2 rounded-xl border border-slate-800 flex justify-center">
              <img
                src={`/uploads/cards/card_${viewCardStudent.student_id}.png`}
                alt="Student ID Card"
                className="rounded-lg shadow-xl max-w-full"
              />
            </div>
            <div className="flex justify-end space-x-2">
              <a
                href={`/uploads/cards/card_${viewCardStudent.student_id}.png`}
                download={`card_${viewCardStudent.student_id}.png`}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold rounded-xl flex items-center space-x-1"
              >
                <span>Download Printable PNG</span>
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
