import React, { useEffect, useState, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useFilterStore } from '../store/filterStore';
import { apiClient } from '../hooks/useApi';
import FilterSidebar from '../components/FilterSidebar';
import Card from '../components/Card';
import Badge from '../components/Badge';
import UpvoteButton from '../components/UpvoteButton';
import Button from '../components/Button';

export default function ResourceVault() {
  const { isAuthenticated } = useAuthStore();
  const { subject, course, search, setSearch } = useFilterStore();
  const navigate = useNavigate();

  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [upvoteLoading, setUpvoteLoading] = useState({});

  // Upload modal state
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadSubject, setUploadSubject] = useState('');
  const [uploadCourse, setUploadCourse] = useState('');
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  // Metadata for upload dropdowns
  const [subjectsList, setSubjectsList] = useState([]);
  const [coursesList, setCoursesList] = useState([]);

  // Fetch resources based on filters
  const fetchResources = useCallback(async () => {
    setLoading(true);
    setError('');

    try {
      const params = {};
      if (subject) params.subject = subject;
      if (course) params.course = course;
      if (search) params.search = search;

      const response = await apiClient.get('/vault/', { params });
      const data = response.data;
      const list = Array.isArray(data) ? data : data.results || [];
      setResources(list);
    } catch (err) {
      console.error('Error fetching vault resources:', err);
      setError('Unable to load resources. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [subject, course, search]);

  useEffect(() => {
    fetchResources();
  }, [fetchResources]);

  // Load subject/course metadata for upload modal
  useEffect(() => {
    async function loadMeta() {
      try {
        const [subjRes, courseRes] = await Promise.all([
          apiClient.get('/core/subjects/'),
          apiClient.get('/core/courses/'),
        ]);
        const subjectsData = Array.isArray(subjRes.data)
          ? subjRes.data
          : subjRes.data.results || [];
        const coursesData = Array.isArray(courseRes.data)
          ? courseRes.data
          : courseRes.data.results || [];
        setSubjectsList(subjectsData);
        setCoursesList(coursesData);
      } catch (e) {
        console.error('Failed to load upload metadata', e);
      }
    }
    loadMeta();
  }, []);

  const handleUpvote = async (id) => {
    if (!isAuthenticated) {
      navigate('/auth');
      return;
    }

    setUpvoteLoading((prev) => ({ ...prev, [id]: true }));
    try {
      const response = await apiClient.post(`/vault/${id}/rate/`);
      const { upvote_count, has_upvoted } = response.data;

      setResources((prev) =>
        prev.map((item) =>
          item.id === id
            ? { ...item, upvote_count, has_upvoted }
            : item
        )
      );
    } catch (err) {
      console.error('Upvote failed:', err);
      if (err.response?.status === 403) {
        alert(err.response.data.message || 'You cannot upvote your own resource.');
      }
    } finally {
      setUpvoteLoading((prev) => ({ ...prev, [id]: false }));
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) {
      setUploadError('Please select a PDF document.');
      return;
    }
    if (!uploadSubject || !uploadCourse) {
      setUploadError('Please select both Subject and Course.');
      return;
    }

    setUploadLoading(true);
    setUploadError('');

    try {
      const formData = new FormData();
      formData.append('title', uploadTitle);
      formData.append('subject', uploadSubject);
      formData.append('course', uploadCourse);
      formData.append('file', uploadFile);

      const response = await apiClient.post('/vault/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Newly uploaded resource starts with PROCESSING status
      const newResource = response.data;
      setResources((prev) => [newResource, ...prev]);

      // Reset form & close modal
      setUploadTitle('');
      setUploadSubject('');
      setUploadCourse('');
      setUploadFile(null);
      setIsUploadOpen(false);
    } catch (err) {
      console.error('Upload failed:', err);
      const msg =
        err.response?.data?.message ||
        (err.response?.data?.file && err.response.data.file[0]) ||
        'Upload failed. Please verify that the file is a PDF.';
      setUploadError(msg);
    } finally {
      setUploadLoading(false);
    }
  };

  const availableUploadCourses = uploadSubject
    ? coursesList.filter((c) => String(c.subject?.id || c.subject) === String(uploadSubject))
    : coursesList;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 font-sans">
      {/* Top Banner & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-bold mb-2 uppercase tracking-wider">
            <span>📚 Digital Library</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            Resource Vault
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Explore lecture notes, exams, and cheat sheets indexed for single-document RAG.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          onClick={() => {
            if (!isAuthenticated) {
              navigate('/auth');
            } else {
              setIsUploadOpen(true);
            }
          }}
          className="self-start md:self-auto"
        >
          <span className="mr-1.5">➕</span> Upload PDF
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Persistent Filter Sidebar */}
        <div className="lg:col-span-1">
          <FilterSidebar />
        </div>

        {/* Resource Feed Area */}
        <div className="lg:col-span-3 space-y-6">
          {/* Search Input Bar */}
          <div className="bg-white p-3 rounded-2xl border border-slate-200/80 shadow-sm flex items-center gap-3">
            <svg
              className="w-5 h-5 text-slate-400 ml-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              type="text"
              placeholder="Search by title, keywords, or topics..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-transparent border-none focus:outline-none text-sm text-slate-800 placeholder:text-slate-400"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="text-xs text-slate-400 hover:text-slate-600 mr-2"
              >
                Clear
              </button>
            )}
          </div>

          {/* Loading / Error States */}
          {loading && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm animate-pulse space-y-4"
                >
                  <div className="flex justify-between">
                    <div className="h-5 bg-slate-100 rounded w-20"></div>
                    <div className="h-5 bg-slate-100 rounded w-16"></div>
                  </div>
                  <div className="h-6 bg-slate-100 rounded w-3/4"></div>
                  <div className="h-4 bg-slate-100 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          )}

          {!loading && error && (
            <div className="bg-rose-50 border border-rose-200 rounded-2xl p-8 text-center text-rose-700">
              <p className="font-semibold text-sm mb-4">{error}</p>
              <Button variant="outline" size="sm" onClick={fetchResources}>
                Retry
              </Button>
            </div>
          )}

          {!loading && !error && resources.length === 0 && (
            <div className="bg-white border border-slate-200/80 rounded-2xl p-12 text-center shadow-sm">
              <div className="w-16 h-16 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center text-2xl mx-auto mb-4">
                📄
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-1">
                No resources found
              </h3>
              <p className="text-slate-500 text-xs max-w-sm mx-auto mb-6">
                Try clearing your search or filter tags, or be the first student to upload notes for this course!
              </p>
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  if (!isAuthenticated) navigate('/auth');
                  else setIsUploadOpen(true);
                }}
              >
                Upload Course PDF
              </Button>
            </div>
          )}

          {/* High-density Resource Grid */}
          {!loading && !error && resources.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {resources.map((res) => (
                <Card
                  key={res.id}
                  className="p-6 flex flex-col justify-between group"
                >
                  <div>
                    {/* Tags & Status Header */}
                    <div className="flex justify-between items-start gap-2 mb-3">
                      <div className="flex flex-wrap items-center gap-1.5">
                        <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-mono text-xs font-bold">
                          {res.course?.code || 'GEN'}
                        </span>
                        {res.subject?.name && (
                          <span className="px-2 py-0.5 rounded-md bg-primary/10 text-primary text-xs font-semibold">
                            {res.subject.name}
                          </span>
                        )}
                      </div>
                      <Badge status={res.status} size="sm" />
                    </div>

                    {/* Title */}
                    <h3 className="font-bold text-slate-900 text-base leading-snug group-hover:text-primary transition-colors line-clamp-2 mb-3">
                      <Link to={`/vault/${res.id}`}>{res.title}</Link>
                    </h3>

                    {/* Metadata & Uploader */}
                    <div className="flex items-center space-x-2 text-xs text-slate-400 mb-4">
                      <span className="inline-flex items-center gap-1 text-rose-500 font-semibold">
                        <svg className="w-3.5 h-3.5" viewBox="0 0 20 20" fill="currentColor">
                          <path
                            fillRule="evenodd"
                            d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                            clipRule="evenodd"
                          />
                        </svg>
                        PDF
                      </span>
                      <span>•</span>
                      <span>By {res.uploader?.full_name || 'Anonymous Student'}</span>
                    </div>
                  </div>

                  {/* Actions footer */}
                  <div className="flex items-center justify-between border-t border-slate-100 pt-4 mt-2">
                    <UpvoteButton
                      count={res.upvote_count || 0}
                      hasUpvoted={res.has_upvoted}
                      loading={upvoteLoading[res.id]}
                      onToggle={() => handleUpvote(res.id)}
                    />

                    <Link
                      to={`/vault/${res.id}`}
                      className="inline-flex items-center space-x-1 text-xs font-bold text-primary hover:text-primary-dark transition-colors"
                    >
                      <span>Explore & Chat</span>
                      <span>&rarr;</span>
                    </Link>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Multipart PDF Upload Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl max-w-lg w-full p-6 sm:p-8 relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-primary to-accent"></div>

            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-black text-slate-900 tracking-tight font-sans">
                Upload Study Resource
              </h3>
              <button
                type="button"
                onClick={() => setIsUploadOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-500 mb-6">
              PDFs are processed into vector embeddings for single-document RAG querying.
            </p>

            {uploadError && (
              <div className="mb-4 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs font-semibold text-rose-700 flex items-center gap-2">
                <svg className="w-4 h-4 flex-shrink-0 text-rose-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span>{uploadError}</span>
              </div>
            )}

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Document Title
                </label>
                <input
                  type="text"
                  required
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  placeholder="e.g. CS101 Final Exam Prep & Review Notes"
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-sm text-slate-800"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Subject
                  </label>
                  <select
                    required
                    value={uploadSubject}
                    onChange={(e) => {
                      setUploadSubject(e.target.value);
                      setUploadCourse('');
                    }}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-primary text-xs font-medium text-slate-800 bg-white"
                  >
                    <option value="">Select Subject</option>
                    {subjectsList.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Course
                  </label>
                  <select
                    required
                    disabled={!uploadSubject}
                    value={uploadCourse}
                    onChange={(e) => setUploadCourse(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-primary text-xs font-medium text-slate-800 bg-white disabled:opacity-50"
                  >
                    <option value="">Select Course</option>
                    {availableUploadCourses.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.code} - {c.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  PDF Document (.pdf only)
                </label>
                <input
                  type="file"
                  required
                  accept=".pdf,application/pdf"
                  onChange={(e) => setUploadFile(e.target.files[0])}
                  className="w-full text-xs text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20 cursor-pointer"
                />
              </div>

              <div className="flex space-x-3 pt-4 border-t border-slate-100">
                <Button
                  type="button"
                  variant="outline"
                  size="md"
                  onClick={() => setIsUploadOpen(false)}
                  className="flex-1"
                  disabled={uploadLoading}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  loading={uploadLoading}
                  className="flex-1"
                >
                  Submit & Ingest
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
