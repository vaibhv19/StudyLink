import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../hooks/useApi';
import Button from '../components/Button';

export default function CreateListing() {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: '',
    condition: 'Used - Good',
    pickupArea: '',
    subject: '',
    course: '',
  });
  const [photoFile, setPhotoFile] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Metadata dropdowns
  const [subjectsList, setSubjectsList] = useState([]);
  const [coursesList, setCoursesList] = useState([]);

  useEffect(() => {
    async function loadMeta() {
      try {
        const [subjRes, courseRes] = await Promise.all([
          apiClient.get('/core/subjects/'),
          apiClient.get('/core/courses/'),
        ]);
        const sData = Array.isArray(subjRes.data)
          ? subjRes.data
          : subjRes.data.results || [];
        const cData = Array.isArray(courseRes.data)
          ? courseRes.data
          : courseRes.data.results || [];
        setSubjectsList(sData);
        setCoursesList(cData);
      } catch (err) {
        console.error('Failed to load listing metadata', err);
      }
    }
    loadMeta();
  }, []);

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPhotoFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!photoFile) {
      setError('Please upload a photo of the physical item.');
      return;
    }
    if (!formData.pickupArea.trim()) {
      setError('Please specify a campus pickup location.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = new FormData();
      data.append('title', formData.title);
      data.append('photo', photoFile);
      data.append('condition', formData.condition);
      data.append('pickup_area', formData.pickupArea);
      if (formData.subject) data.append('subject', formData.subject);
      if (formData.course) data.append('course', formData.course);

      const response = await apiClient.post('/market/', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      navigate(`/market/${response.data.id}`);
    } catch (err) {
      console.error('Listing creation error:', err);
      const msg =
        err.response?.data?.message ||
        (err.response?.data?.photo && err.response.data.photo[0]) ||
        'Failed to create listing. Please verify all required fields.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const availableCourses = formData.subject
    ? coursesList.filter((c) => String(c.subject?.id || c.subject) === String(formData.subject))
    : coursesList;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 font-sans">
      <div className="mb-6 flex items-center space-x-2 text-xs text-slate-400">
        <Link to="/market" className="hover:text-primary transition-colors">
          &larr; Back to Marketplace
        </Link>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200/80 p-8 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-accent to-primary"></div>

        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-accent/10 text-accent flex items-center justify-center font-bold text-xl">
            📦
          </div>
          <div>
            <h1 className="text-2xl font-black text-slate-900 tracking-tight">
              Create Giveaway Listing
            </h1>
            <p className="text-xs text-slate-500">
              Pass along textbooks, calculators, and lab tools to students in need.
            </p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-3.5 bg-rose-50 border border-rose-200 rounded-xl text-xs font-semibold text-rose-700 flex items-center gap-2">
            <svg className="w-4 h-4 flex-shrink-0 text-rose-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Item Title
            </label>
            <input
              type="text"
              required
              placeholder="e.g. TI-84 Plus CE Graphing Calculator or Chemistry Lab Coat"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent text-sm text-slate-800"
            />
          </div>

          {/* Photo Upload & Live Preview */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Item Photo
            </label>
            <div className="flex flex-col sm:flex-row items-center gap-6 p-4 rounded-xl border border-dashed border-slate-300 bg-slate-50/50">
              {photoPreview ? (
                <div className="w-32 h-32 rounded-xl overflow-hidden border border-slate-200 flex-shrink-0 bg-white">
                  <img
                    src={photoPreview}
                    alt="Preview"
                    className="w-full h-full object-cover"
                  />
                </div>
              ) : (
                <div className="w-32 h-32 rounded-xl border border-slate-200 bg-white flex flex-col items-center justify-center text-slate-400 text-xs flex-shrink-0">
                  <span className="text-2xl mb-1">📷</span>
                  <span>No Photo</span>
                </div>
              )}
              <div className="space-y-2 flex-grow">
                <input
                  type="file"
                  required
                  accept="image/*"
                  onChange={handlePhotoChange}
                  className="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-accent/10 file:text-accent hover:file:bg-accent/20 cursor-pointer"
                />
                <p className="text-xxs text-slate-400">
                  High quality photos help peers verify condition before requesting pickup.
                </p>
              </div>
            </div>
          </div>

          {/* Condition & Pickup Area */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Condition
              </label>
              <select
                value={formData.condition}
                onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent text-xs font-medium text-slate-800 bg-white"
              >
                <option value="New">New</option>
                <option value="Used - Like New">Used - Like New</option>
                <option value="Used - Good">Used - Good</option>
                <option value="Used - Fair">Used - Fair</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Campus Pickup Area
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Science Library Lobby or Student Center"
                value={formData.pickupArea}
                onChange={(e) => setFormData({ ...formData, pickupArea: e.target.value })}
                className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent text-sm text-slate-800"
              />
            </div>
          </div>

          {/* Subject & Course (Optional associations) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Related Subject (Optional)
              </label>
              <select
                value={formData.subject}
                onChange={(e) => setFormData({ ...formData, subject: e.target.value, course: '' })}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent text-xs font-medium text-slate-800 bg-white"
              >
                <option value="">None / General</option>
                {subjectsList.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                Related Course (Optional)
              </label>
              <select
                disabled={!formData.subject}
                value={formData.course}
                onChange={(e) => setFormData({ ...formData, course: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent text-xs font-medium text-slate-800 bg-white disabled:opacity-50"
              >
                <option value="">None / All</option>
                {availableCourses.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.code} - {c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex space-x-3 pt-4 border-t border-slate-100">
            <Link to="/market" className="flex-1">
              <Button type="button" variant="outline" size="md" className="w-full">
                Cancel
              </Button>
            </Link>
            <Button
              type="submit"
              variant="secondary"
              size="md"
              loading={loading}
              className="flex-1"
            >
              Publish Giveaway
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
