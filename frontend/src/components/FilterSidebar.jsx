import React, { useEffect, useState } from 'react';
import { useFilterStore } from '../store/filterStore';
import { apiClient } from '../hooks/useApi';

export default function FilterSidebar({ className = '' }) {
  const {
    subject,
    course,
    setSubject,
    setCourse,
    resetVaultFilters,
  } = useFilterStore();

  const [subjectsList, setSubjectsList] = useState([]);
  const [coursesList, setCoursesList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    async function loadMetadata() {
      try {
        const [subjRes, courseRes] = await Promise.all([
          apiClient.get('/core/subjects/', { params: { page_size: 100 } }),
          apiClient.get('/core/courses/', { params: { page_size: 100 } }),
        ]);

        if (isMounted) {
          const subjectsData = Array.isArray(subjRes.data)
            ? subjRes.data
            : subjRes.data.results || [];
          const coursesData = Array.isArray(courseRes.data)
            ? courseRes.data
            : courseRes.data.results || [];

          setSubjectsList(subjectsData);
          setCoursesList(coursesData);
        }
      } catch (err) {
        console.error('Failed to load filter metadata', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadMetadata();

    return () => {
      isMounted = false;
    };
  }, []);

  const filteredCourses = subject
    ? coursesList.filter((c) => c.subject?.slug === subject)
    : coursesList;

  const hasActiveFilters = !!subject || !!course;

  return (
    <aside className={`bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-6 ${className}`}>
      <div className="flex items-center justify-between border-b border-slate-100 pb-4">
        <div className="flex items-center space-x-2">
          <span className="text-slate-400">⚡</span>
          <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wider">
            Filters
          </h3>
        </div>
        {hasActiveFilters && (
          <button
            type="button"
            onClick={resetVaultFilters}
            className="text-xs text-primary hover:text-primary-dark font-semibold transition-colors"
          >
            Reset
          </button>
        )}
      </div>

      {loading ? (
        <div className="space-y-4 py-4 animate-pulse">
          <div className="h-4 bg-slate-100 rounded w-1/2"></div>
          <div className="h-8 bg-slate-100 rounded"></div>
          <div className="h-4 bg-slate-100 rounded w-1/2 mt-4"></div>
          <div className="h-8 bg-slate-100 rounded"></div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Subject Filter */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
              Subject
            </label>
            <div className="flex flex-wrap gap-1.5">
              <button
                type="button"
                onClick={() => {
                  setSubject('');
                  setCourse('');
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  !subject
                    ? 'bg-primary text-white shadow-xs shadow-primary/20'
                    : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200/60'
                }`}
              >
                All Subjects
              </button>
              {subjectsList.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => {
                    if (subject === s.slug) {
                      setSubject('');
                      setCourse('');
                    } else {
                      setSubject(s.slug);
                      setCourse('');
                    }
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    subject === s.slug
                      ? 'bg-primary text-white shadow-xs shadow-primary/20'
                      : 'bg-slate-50 hover:bg-slate-100 text-slate-600 border border-slate-200/60'
                  }`}
                >
                  {s.name}
                </button>
              ))}
            </div>
          </div>

          {/* Course Filter */}
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
              Course Code
            </label>
            {filteredCourses.length === 0 ? (
              <p className="text-xs text-slate-400 italic">No courses found</p>
            ) : (
              <div className="space-y-1 max-h-48 overflow-y-auto pr-1">
                {filteredCourses.map((c) => (
                  <label
                    key={c.id}
                    className={`flex items-center space-x-2.5 p-2 rounded-lg text-xs font-medium cursor-pointer transition-colors ${
                      course === c.code
                        ? 'bg-primary/10 text-primary font-bold'
                        : 'text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="courseFilter"
                      checked={course === c.code}
                      onChange={() => setCourse(c.code)}
                      className="text-primary focus:ring-primary h-3.5 w-3.5"
                    />
                    <span className="font-mono text-slate-700">{c.code}</span>
                    <span className="truncate text-slate-400">— {c.name}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </aside>
  );
}
