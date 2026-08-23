import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../hooks/useApi';
import Button from '../components/Button';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});

  const { login } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  const fromPath = location.state?.from?.pathname || '/dashboard';

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    if (fieldErrors[e.target.name]) {
      setFieldErrors({
        ...fieldErrors,
        [e.target.name]: null,
      });
    }
    setErrorMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');
    setFieldErrors({});

    try {
      if (isLogin) {
        const response = await apiClient.post('/auth/login/', {
          email: formData.email,
          password: formData.password,
        });

        login(response.data.user, response.data.access);
        navigate(fromPath, { replace: true });
      } else {
        const response = await apiClient.post('/auth/register/', {
          full_name: formData.fullName,
          email: formData.email,
          password: formData.password,
        });

        login(response.data.user, response.data.access);
        navigate(fromPath, { replace: true });
      }
    } catch (err) {
      if (err.response?.data) {
        const data = err.response.data;
        if (data.message) {
          setErrorMessage(data.message);
        }
        if (data.fields) {
          setFieldErrors(data.fields);
        }
      } else {
        setErrorMessage('Unable to connect to server. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-[#11151A] text-[#E9EAEC] font-sans">
      {/* Left Panel: StudyLink Product Positioning & Core Capabilities */}
      <div className="lg:w-1/2 bg-[#151A22] border-b lg:border-b-0 lg:border-r border-[#313645] p-8 sm:p-12 lg:p-16 flex flex-col justify-between">
        <div>
          {/* Brand Mark */}
          <Link to="/" className="inline-flex items-center gap-2 text-[#E9EAEC] font-bold text-base tracking-tight mb-10">
            <span className="w-6 h-6 rounded bg-[#4A4E98] text-[#E9EAEC] flex items-center justify-center text-xs font-bold">S</span>
            <span>StudyLink</span>
          </Link>

          {/* Product Statement */}
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-[#E9EAEC] tracking-tight leading-[1.18] mb-3.5 max-w-md font-sans">
            Your campus library, shared by students.
          </h1>
          <p className="text-[#979DA5] text-sm leading-relaxed mb-10 max-w-md">
            StudyLink connects students to share study materials, ask document-grounded questions about lecture notes, and exchange campus gear.
          </p>

          {/* Core Capabilities */}
          <div className="space-y-6 pt-6 border-t border-[#313645]">
            <div className="text-[11px] font-bold uppercase tracking-widest text-[#979DA5]">
              Core Capabilities
            </div>

            {/* Capability 1: Resource Vault */}
            <div className="flex items-start space-x-3.5">
              <div className="w-8 h-8 rounded bg-[#1A202A] border border-[#313645] text-[#6489E7] flex items-center justify-center shrink-0 mt-0.5">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-[#E9EAEC]">Resource Vault</h2>
                <p className="text-xs text-[#979DA5] leading-relaxed mt-0.5">
                  Find and share lecture notes, study material, and academic resources.
                </p>
              </div>
            </div>

            {/* Capability 2: Document Q&A */}
            <div className="flex items-start space-x-3.5">
              <div className="w-8 h-8 rounded bg-[#1A202A] border border-[#313645] text-[#539C5F] flex items-center justify-center shrink-0 mt-0.5">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-[#E9EAEC]">Document Q&amp;A</h2>
                <p className="text-xs text-[#979DA5] leading-relaxed mt-0.5">
                  Ask questions about uploaded PDFs and get document-grounded answers.
                </p>
              </div>
            </div>

            {/* Capability 3: Campus Marketplace */}
            <div className="flex items-start space-x-3.5">
              <div className="w-8 h-8 rounded bg-[#1A202A] border border-[#313645] text-[#F2A906] flex items-center justify-center shrink-0 mt-0.5">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
              </div>
              <div>
                <h2 className="text-sm font-semibold text-[#E9EAEC]">Campus Marketplace</h2>
                <p className="text-xs text-[#979DA5] leading-relaxed mt-0.5">
                  Trade or give away useful books, calculators, and campus equipment.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Left Bottom Footer */}
        <div className="pt-10 text-xs text-[#575D65]">
          &copy; {new Date().getFullYear()} StudyLink
        </div>
      </div>

      {/* Right Panel: Authentication Form */}
      <div className="lg:w-1/2 bg-[#11151A] p-8 sm:p-12 lg:p-16 flex flex-col justify-center items-center">
        <div className="max-w-sm w-full space-y-6">
          {/* Header */}
          <div>
            <div className="text-[11px] font-bold uppercase tracking-widest text-[#979DA5] mb-1">
              Account Access
            </div>
            <h2 className="text-2xl font-bold text-[#E9EAEC] tracking-tight font-sans">
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>
            <p className="mt-1 text-xs text-[#979DA5] leading-relaxed">
              {isLogin
                ? 'Sign in to access your study resources and campus marketplace.'
                : 'Create an account to upload notes, ask questions, and trade campus gear.'}
            </p>
          </div>

          {/* Restrained Tab Switcher */}
          <div className="flex border-b border-[#313645] space-x-6">
            <button
              type="button"
              onClick={() => {
                setIsLogin(true);
                setErrorMessage('');
                setFieldErrors({});
              }}
              className={`pb-2.5 text-xs font-bold uppercase tracking-wider transition-colors relative ${
                isLogin
                  ? 'text-[#E9EAEC] border-b-2 border-[#565DDE] -mb-px'
                  : 'text-[#979DA5] hover:text-[#E9EAEC]'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setIsLogin(false);
                setErrorMessage('');
                setFieldErrors({});
              }}
              className={`pb-2.5 text-xs font-bold uppercase tracking-wider transition-colors relative ${
                !isLogin
                  ? 'text-[#E9EAEC] border-b-2 border-[#565DDE] -mb-px'
                  : 'text-[#979DA5] hover:text-[#E9EAEC]'
              }`}
            >
              Register
            </button>
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div className="p-3 bg-rose-950/40 border border-rose-800/80 rounded text-xs font-medium text-rose-300 flex items-center gap-2">
              <svg className="w-4 h-4 flex-shrink-0 text-rose-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Form */}
          <form className="space-y-4" onSubmit={handleSubmit}>
            {!isLogin && (
              <div>
                <label className="block text-[11px] font-bold text-[#E9EAEC] uppercase tracking-wider mb-1.5">
                  Full Name
                </label>
                <input
                  type="text"
                  name="fullName"
                  required
                  value={formData.fullName}
                  onChange={handleChange}
                  placeholder="Alex Morgan"
                  className="w-full px-3.5 py-2.5 rounded bg-[#151A22] border border-[#313645] text-sm text-[#E9EAEC] placeholder-[#575D65] focus:outline-none focus:border-[#565DDE] transition-colors"
                />
                {fieldErrors.full_name && (
                  <p className="mt-1 text-xs text-rose-400 font-medium">
                    {Array.isArray(fieldErrors.full_name) ? fieldErrors.full_name[0] : fieldErrors.full_name}
                  </p>
                )}
              </div>
            )}

            <div>
              <label className="block text-[11px] font-bold text-[#E9EAEC] uppercase tracking-wider mb-1.5">
                Email Address
              </label>
              <input
                type="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                placeholder="student@university.edu"
                className="w-full px-3.5 py-2.5 rounded bg-[#151A22] border border-[#313645] text-sm text-[#E9EAEC] placeholder-[#575D65] focus:outline-none focus:border-[#565DDE] transition-colors"
              />
              {fieldErrors.email && (
                <p className="mt-1 text-xs text-rose-400 font-medium">
                  {Array.isArray(fieldErrors.email) ? fieldErrors.email[0] : fieldErrors.email}
                </p>
              )}
            </div>

            <div>
              <label className="block text-[11px] font-bold text-[#E9EAEC] uppercase tracking-wider mb-1.5">
                Password
              </label>
              <input
                type="password"
                name="password"
                required
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 rounded bg-[#151A22] border border-[#313645] text-sm text-[#E9EAEC] placeholder-[#575D65] focus:outline-none focus:border-[#565DDE] transition-colors"
              />
              {fieldErrors.password && (
                <p className="mt-1 text-xs text-rose-400 font-medium">
                  {Array.isArray(fieldErrors.password) ? fieldErrors.password[0] : fieldErrors.password}
                </p>
              )}
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              loading={loading}
              className="w-full mt-2 bg-[#565DDE] hover:bg-[#4A4E98] text-[#E9EAEC] rounded font-semibold text-xs uppercase tracking-wider py-2.5 transition-colors duration-150 shadow-none border border-[#565DDE]/20"
            >
              {isLogin ? 'Sign In' : 'Create Account'}
            </Button>
          </form>

          {/* Return Home Link */}
          <div className="pt-4 border-t border-[#313645] text-center">
            <Link
              to="/"
              className="text-xs text-[#575D65] hover:text-[#979DA5] inline-flex items-center gap-1.5 transition-colors"
            >
              <span aria-hidden="true">&larr;</span>
              <span>Back to StudyLink</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
