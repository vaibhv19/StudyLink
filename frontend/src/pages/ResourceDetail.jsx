import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../hooks/useApi';
import PdfViewer from '../components/PdfViewer';
import RagChatPanel from '../components/RagChatPanel';
import DoubtBoard from '../components/DoubtBoard';
import Badge from '../components/Badge';
import UpvoteButton from '../components/UpvoteButton';
import Button from '../components/Button';

export default function ResourceDetail() {
  const { id } = useParams();
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  const [resource, setResource] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [targetPage, setTargetPage] = useState(1);
  const [upvoteLoading, setUpvoteLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function loadResource() {
      setLoading(true);
      setError('');
      try {
        const response = await apiClient.get(`/vault/${id}/`);
        if (isMounted) {
          setResource(response.data);
        }
      } catch (err) {
        console.error('Failed to load resource detail', err);
        if (isMounted) {
          setError('Resource not found or failed to load.');
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadResource();

    return () => {
      isMounted = false;
    };
  }, [id]);

  const handleUpvote = async () => {
    if (!isAuthenticated) {
      navigate('/auth');
      return;
    }

    setUpvoteLoading(true);
    try {
      const response = await apiClient.post(`/vault/${id}/rate/`);
      const { upvote_count, has_upvoted } = response.data;
      setResource((prev) => ({
        ...prev,
        upvote_count,
        has_upvoted,
      }));
    } catch (err) {
      console.error('Upvote failed', err);
      if (err.response?.status === 403) {
        alert(err.response.data.message || 'You cannot upvote your own resource.');
      }
    } finally {
      setUpvoteLoading(false);
    }
  };

  const handleCitationJump = (pageNumber) => {
    if (pageNumber) {
      setTargetPage(pageNumber);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-sm font-semibold text-slate-500">Loading document...</p>
      </div>
    );
  }

  if (error || !resource) {
    return (
      <div className="max-w-md mx-auto my-16 p-8 bg-white rounded-2xl border border-slate-200 text-center shadow-sm">
        <div className="w-12 h-12 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center text-xl font-bold mx-auto mb-4">
          ✕
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Resource Unavailable</h2>
        <p className="text-xs text-slate-500 mb-6">{error || 'Could not find this resource.'}</p>
        <Link to="/vault">
          <Button variant="primary" size="md" className="w-full">
            Back to Resource Vault
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 font-sans">
      {/* Top Breadcrumb & Metadata Header */}
      <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-slate-400 mb-2">
            <Link to="/vault" className="hover:text-primary transition-colors">
              &larr; Vault
            </Link>
            <span>/</span>
            <span className="text-slate-600 font-medium">
              {resource.subject?.name || 'General'}
            </span>
            <span>/</span>
            <span className="font-mono text-primary font-bold">
              {resource.course?.code || 'CS'}
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
              {resource.title}
            </h1>
            <Badge status={resource.status} size="sm" />
          </div>

          <p className="text-xs text-slate-500 mt-1">
            Uploaded by {resource.uploader?.full_name || 'Anonymous Student'} •{' '}
            {resource.course?.name || ''}
          </p>
        </div>

        <div className="flex items-center space-x-3 self-start md:self-auto">
          <UpvoteButton
            count={resource.upvote_count || 0}
            hasUpvoted={resource.has_upvoted}
            loading={upvoteLoading}
            onToggle={handleUpvote}
          />

          {resource.file_path && (
            <a
              href={resource.file_path}
              target="_blank"
              rel="noopener noreferrer"
              download
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition-colors inline-flex items-center gap-1.5"
            >
              <span>⬇ Download PDF</span>
            </a>
          )}
        </div>
      </div>

      {/* Split PDF Viewer (70%) + RAG Chat Panel (30%) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left 70%: PDF Viewer (8 columns on lg) */}
        <div className="lg:col-span-8 h-[650px] lg:h-[780px]">
          <PdfViewer
            url={resource.file_path}
            targetPage={targetPage}
            onPageChange={(page) => setTargetPage(page)}
          />
        </div>

        {/* Right 30%: RAG Chat Panel (4 columns on lg) */}
        <div className="lg:col-span-4 h-[650px] lg:h-[780px]">
          <RagChatPanel
            resourceId={resource.id}
            resourceStatus={resource.status}
            onCitationClick={handleCitationJump}
          />
        </div>
      </div>

      {/* Doubt Board Threaded Comments Section */}
      <DoubtBoard
        resourceId={resource.id}
        resourceUploaderId={resource.uploader?.id}
      />
    </div>
  );
}
