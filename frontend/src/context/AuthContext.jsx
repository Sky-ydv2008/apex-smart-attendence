import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [teacher, setTeacher] = useState(() => {
    const saved = localStorage.getItem('attendai_teacher');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('attendai_token');
    if (token) {
      authAPI.getMe()
        .then((res) => {
          setTeacher(res.data);
          localStorage.setItem('attendai_teacher', JSON.stringify(res.data));
        })
        .catch(() => {
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await authAPI.login(email, password);
    const { access_token, teacher: teacherData } = res.data;
    localStorage.setItem('attendai_token', access_token);
    localStorage.setItem('attendai_teacher', JSON.stringify(teacherData));
    setTeacher(teacherData);
    return teacherData;
  };

  const quickDemoLogin = async () => {
    return login('teacher@apex.edu', 'admin123');
  };

  const logout = () => {
    localStorage.removeItem('attendai_token');
    localStorage.removeItem('attendai_teacher');
    setTeacher(null);
  };

  return (
    <AuthContext.Provider value={{ teacher, login, quickDemoLogin, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
