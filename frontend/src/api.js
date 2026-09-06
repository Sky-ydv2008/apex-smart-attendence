import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('attendai_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401 unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('attendai_token');
      localStorage.removeItem('attendai_teacher');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

export const authAPI = {
  login: (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getMe: () => api.get('/auth/me'),
};

export const classesAPI = {
  getAll: () => api.get('/classes'),
  create: (data) => api.post('/classes', data),
  delete: (id) => api.delete(`/classes/${id}`),
};

export const studentsAPI = {
  getAll: (params) => api.get('/students', { params }),
  create: (data) => api.post('/students', data),
  enrollFace: (id, formData) =>
    api.post(`/students/${id}/enroll-face`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  getIDCard: (id) => api.get(`/students/${id}/id-card`),
  delete: (id) => api.delete(`/students/${id}`),
};

export const sessionsAPI = {
  getAll: () => api.get('/sessions'),
  create: (data) => api.post('/sessions', data),
  start: (id) => api.post(`/sessions/${id}/start`),
  stop: (id) => api.post(`/sessions/${id}/stop`),
};

export const attendanceAPI = {
  scan: (session_id, image_base64) =>
    api.post('/attendance/scan', { session_id, image_base64 }),
  demoScan: (session_id, student_id_code) =>
    api.post(`/attendance/demo-scan?session_id=${session_id}&student_id_code=${student_id_code}`),
  getBySession: (session_id) => api.get(`/attendance/session/${session_id}`),
  override: (data) => api.post('/attendance/override', data),
};

export const reportsAPI = {
  getSummary: () => api.get('/reports/summary'),
  getDaily: (date) => api.get('/reports/daily', { params: { date } }),
  getCSVUrl: (date, class_id) => `/api/reports/export/csv?${new URLSearchParams({ date: date || '', class_id: class_id || '' })}`,
  getExcelUrl: (date, class_id) => `/api/reports/export/excel?${new URLSearchParams({ date: date || '', class_id: class_id || '' })}`,
  getPDFUrl: (date, class_id) => `/api/reports/export/pdf?${new URLSearchParams({ date: date || '', class_id: class_id || '' })}`,
};
