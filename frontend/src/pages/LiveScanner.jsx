import React, { useState, useEffect, useRef } from 'react';
import { sessionsAPI, attendanceAPI, studentsAPI } from '../api';
import confetti from 'canvas-confetti';
import {
  Camera,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Zap,
  RefreshCw,
  Upload,
  User,
  AlertTriangle,
  Play,
  Square
} from 'lucide-react';

export default function LiveScanner({ selectedSessionId }) {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(selectedSessionId || '');
  const [students, setStudents] = useState([]);
  const [selectedStudentCode, setSelectedStudentCode] = useState('');
  
  const [scanning, setScanning] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);

  // Load Sessions and Enrolled Students
  useEffect(() => {
    sessionsAPI.getAll().then((res) => {
      setSessions(res.data);
      if (!currentSessionId && res.data.length > 0) {
        const active = res.data.find((s) => s.status === 'active');
        setCurrentSessionId(active ? active.id : res.data[0].id);
      }
    });

    studentsAPI.getAll().then((res) => {
      setStudents(res.data);
      if (res.data.length > 0) {
        setSelectedStudentCode(res.data[0].student_id);
      }
    });
  }, []);

  // WebCam Camera Setup
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      streamRef.current = stream;
      setScanning(true);
    } catch (err) {
      console.error('Camera access error:', err);
      alert('Could not access webcam. Please check camera permissions.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    clearInterval(intervalRef.current);
    setScanning(false);
  };

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  // Capture video frame and send to backend scan endpoint
  const captureAndScan = async () => {
    if (!videoRef.current || !canvasRef.current || !currentSessionId) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const image_base64 = canvas.toDataURL('image/jpeg', 0.85);

    setLoading(true);
    try {
      const res = await attendanceAPI.scan(currentSessionId, image_base64);
      setLastResult(res.data);

      if (res.data.success) {
        confetti({ particleCount: 50, spread: 60, origin: { y: 0.7 } });
      }
    } catch (err) {
      console.error('Scan error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Instant Demo Scan Simulation
  const triggerDemoScan = async () => {
    if (!currentSessionId || !selectedStudentCode) {
      alert('Please select an active session and student for demo scan.');
      return;
    }

    setLoading(true);
    try {
      const res = await attendanceAPI.demoScan(currentSessionId, selectedStudentCode);
      setLastResult(res.data);

      if (res.data.success) {
        confetti({ particleCount: 75, spread: 70, origin: { y: 0.6 } });
      }
    } catch (err) {
      console.error('Demo scan error:', err);
      setLastResult({
        success: false,
        message: err.response?.data?.detail || 'Demo scan rejected',
        card_verified: false,
        face_matched: false,
        overall_confidence: 0,
        status: 'REJECTED'
      });
    } finally {
      setLoading(false);
    }
  };

  // File Upload Scan Fallback
  const handleFileUploadScan = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (evt) => {
      const base64 = evt.target.result;
      setLoading(true);
      try {
        const res = await attendanceAPI.scan(currentSessionId, base64);
        setLastResult(res.data);
        if (res.data.success) {
          confetti({ particleCount: 50, spread: 60, origin: { y: 0.7 } });
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    reader.readAsDataURL(file);
  };

  const activeSessObj = sessions.find((s) => s.id === Number(currentSessionId));

  return (
    <div className="space-y-6">
      {/* Session Selector Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center font-bold">
            <Camera className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Live AI Verification Camera Studio</h2>
            <p className="text-xs text-slate-400">ID-Card OCR + Enrolled Face Similarity Check</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <select
            value={currentSessionId}
            onChange={(e) => setCurrentSessionId(e.target.value)}
            className="px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm font-semibold text-white focus:outline-none focus:border-indigo-500"
          >
            {sessions.map((s) => (
              <option key={s.id} value={s.id}>
                Session #{s.id}: {s.class_name} — {s.subject_code} ({s.status.toUpperCase()})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Studio View: Video Canvas + Two-Factor Result Display */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Camera Feed */}
        <div className="lg:col-span-7 space-y-4">
          <div className="relative rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden shadow-2xl aspect-video flex items-center justify-center">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`w-full h-full object-cover ${!scanning ? 'hidden' : ''}`}
            />
            <canvas ref={canvasRef} className="hidden" />

            {/* Scanning Overlay Bounding Box */}
            {scanning && (
              <div className="absolute inset-0 pointer-events-none border-2 border-indigo-500/30 m-8 rounded-2xl flex flex-col justify-between p-4">
                <div className="flex justify-between text-xs text-indigo-400 font-mono">
                  <span>[ID CARD SCAN ZONE]</span>
                  <span>FPS: 30 | AI READY</span>
                </div>
                <div className="w-48 h-28 mx-auto border-2 border-dashed border-emerald-400/80 rounded-xl flex items-center justify-center bg-emerald-500/5">
                  <span className="text-[10px] font-bold text-emerald-300 uppercase tracking-widest">Hold Card Here</span>
                </div>
                <div className="flex justify-between text-xs text-indigo-400 font-mono">
                  <span>FACE TRACKING: ON</span>
                  <span>100% OFFLINE</span>
                </div>
              </div>
            )}

            {!scanning && (
              <div className="text-center p-8 space-y-4">
                <div className="w-16 h-16 rounded-full bg-slate-900 border border-slate-800 text-slate-500 flex items-center justify-center mx-auto">
                  <Camera className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-300">Camera Feed Paused</h3>
                  <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
                    Click "Start Local Camera" or use the Hackathon Instant Demo Scan simulator below.
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Camera Action Buttons */}
          <div className="flex items-center space-x-3">
            {!scanning ? (
              <button
                onClick={startCamera}
                className="flex-1 py-3 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl flex items-center justify-center space-x-2 transition-all cursor-pointer"
              >
                <Play className="w-4 h-4" />
                <span>Start Local Camera</span>
              </button>
            ) : (
              <>
                <button
                  onClick={captureAndScan}
                  disabled={loading}
                  className="flex-1 py-3 px-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl flex items-center justify-center space-x-2 transition-all cursor-pointer disabled:opacity-50"
                >
                  <Camera className="w-4 h-4" />
                  <span>{loading ? 'Processing Frame...' : 'Scan Frame Now'}</span>
                </button>
                <button
                  onClick={stopCamera}
                  className="py-3 px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl flex items-center space-x-1 cursor-pointer"
                >
                  <Square className="w-4 h-4" />
                  <span>Stop</span>
                </button>
              </>
            )}

            <label className="py-3 px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold rounded-xl flex items-center space-x-2 cursor-pointer border border-slate-700">
              <Upload className="w-4 h-4" />
              <span>Upload Photo</span>
              <input type="file" accept="image/*" onChange={handleFileUploadScan} className="hidden" />
            </label>
          </div>
        </div>

        {/* Right Column: Two-Factor Identity Verification Result Panel */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-6 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold text-white flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-indigo-400" />
                <span>Verification Verdict</span>
              </h3>
              <span className="text-xs text-indigo-400 font-mono font-semibold">2-FACTOR AI</span>
            </div>

            {lastResult ? (
              <div className="space-y-5">
                {/* PDF Specified Exact Result Box Format */}
                <div
                  className={`p-5 rounded-2xl border ${
                    lastResult.success
                      ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-200'
                      : 'bg-rose-950/40 border-rose-500/50 text-rose-200'
                  } space-y-3`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold uppercase tracking-wider">Attendance Status</span>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-extrabold tracking-wider ${
                        lastResult.success ? 'bg-emerald-500 text-slate-950' : 'bg-rose-500 text-white'
                      }`}
                    >
                      {lastResult.status}
                    </span>
                  </div>

                  {/* PDF Key Line: ID Card: Verified | Face: Matched | Confidence: 96.4% */}
                  <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-2 text-xs font-mono">
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">ID Card OCR:</span>
                      <strong className={lastResult.card_verified ? 'text-emerald-400' : 'text-rose-400'}>
                        {lastResult.card_verified ? 'ID Card: Verified ✓' : 'Failed ✗'}
                      </strong>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-slate-400">Face Vector:</span>
                      <strong className={lastResult.face_matched ? 'text-emerald-400' : 'text-rose-400'}>
                        {lastResult.face_matched ? 'Face: Matched ✓' : 'Mismatch ✗'}
                      </strong>
                    </div>
                    <div className="flex justify-between items-center pt-2 border-t border-slate-800 text-sm">
                      <span className="text-slate-300 font-sans font-semibold">Confidence:</span>
                      <strong className="text-purple-400 font-bold">
                        {lastResult.overall_confidence.toFixed(1)}%
                      </strong>
                    </div>
                  </div>

                  <p className="text-sm font-semibold leading-snug">{lastResult.message}</p>
                </div>

                {lastResult.student_name && (
                  <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-800 space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Student Name:</span>
                      <strong className="text-white text-sm">{lastResult.student_name}</strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Student ID:</span>
                      <strong className="text-indigo-400 font-mono">{lastResult.student_id}</strong>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Class:</span>
                      <strong className="text-slate-200">{lastResult.class_name || activeSessObj?.class_name}</strong>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-10 text-slate-500 space-y-2">
                <ShieldCheck className="w-12 h-12 mx-auto text-slate-700" />
                <p className="text-sm font-medium">Ready for scan input</p>
                <p className="text-xs text-slate-600">Scan card + face or run demo simulation below.</p>
              </div>
            )}
          </div>

          {/* Hackathon Instant Demo Scan Panel */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-indigo-950/60 to-purple-950/40 border border-indigo-500/30 space-y-4">
            <div className="flex items-center space-x-2 text-indigo-300 font-bold text-sm">
              <Zap className="w-4 h-4 text-indigo-400 fill-indigo-400" />
              <span>Hackathon Demo Scan Simulator</span>
            </div>
            <p className="text-xs text-slate-300">
              Instantly simulate high-precision verification scan for any student without needing physical card in frame!
            </p>

            <div className="space-y-3">
              <select
                value={selectedStudentCode}
                onChange={(e) => setSelectedStudentCode(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs font-semibold text-white focus:outline-none focus:border-indigo-500"
              >
                {students.map((st) => (
                  <option key={st.id} value={st.student_id}>
                    {st.name} ({st.student_id}) — {st.class_name}
                  </option>
                ))}
              </select>

              <button
                onClick={triggerDemoScan}
                disabled={loading}
                className="w-full py-3 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl text-xs shadow-lg shadow-emerald-600/20 flex items-center justify-center space-x-2 cursor-pointer"
              >
                <Zap className="w-4 h-4 fill-white" />
                <span>Simulate Instant 2-Factor AI Verification Scan</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
