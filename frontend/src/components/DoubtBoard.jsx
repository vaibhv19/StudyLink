import React, { useEffect, useState, useCallback } from 'react';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../hooks/useApi';
import Button from './Button';

export default function DoubtBoard({ resourceId, resourceUploaderId }) {
  const { user, isAuthenticated } = useAuthStore();
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newCommentText, setNewCommentText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [replyingTo, setReplyingTo] = useState(null); // comment id
  const [replyText, setReplyText] = useState('');

  const fetchComments = useCallback(async () => {
    if (!resourceId) return;
    try {
      const response = await apiClient.get(`/vault/${resourceId}/comments/`);
      const data = Array.isArray(response.data)
        ? response.data
        : response.data.results || [];
      setComments(data);
    } catch (err) {
      console.error('Failed to load doubt board comments', err);
    } finally {
      setLoading(false);
    }
  }, [resourceId]);

  useEffect(() => {
    fetchComments();
  }, [fetchComments]);

  const handleCreateComment = async (e) => {
    e.preventDefault();
    if (!newCommentText.trim() || submitting) return;

    setSubmitting(true);
    try {
      const response = await apiClient.post(`/vault/${resourceId}/comments/`, {
        content: newCommentText.trim(),
      });
      setComments((prev) => [...prev, response.data]);
      setNewCommentText('');
    } catch (err) {
      console.error('Comment creation failed', err);
      alert('Failed to post comment. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateReply = async (parentId) => {
    if (!replyText.trim() || submitting) return;

    setSubmitting(true);
    try {
      const response = await apiClient.post(`/vault/${resourceId}/comments/`, {
        parent: parentId,
        content: replyText.trim(),
      });

      // Update parent's replies list in state
      setComments((prev) =>
        prev.map((c) => {
          if (c.id === parentId) {
            return {
              ...c,
              replies: [...(c.replies || []), response.data],
            };
          }
          return c;
        })
      );
      setReplyText('');
      setReplyingTo(null);
    } catch (err) {
      console.error('Reply creation failed', err);
      alert('Failed to post reply.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleSolved = async (commentId, currentSolved) => {
    try {
      const response = await apiClient.patch(`/vault/comments/${commentId}/`, {
        is_solved: !currentSolved,
      });

      const updated = response.data;
      setComments((prev) =>
        prev.map((c) => (c.id === commentId ? { ...c, is_solved: updated.is_solved } : c))
      );
    } catch (err) {
      console.error('Solved toggle failed', err);
    }
  };

  const canToggleSolved = (comment) => {
    if (!user) return false;
    return (
      String(user.id) === String(comment.user?.id) ||
      String(user.id) === String(resourceUploaderId)
    );
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-6 sm:p-8 shadow-sm">
      <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-primary font-bold">💬</span>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">
              Doubt Board
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Peer questions, corrections, and lecture clarifications.
          </p>
        </div>
        <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 text-xs font-semibold">
          {comments.length} Threads
        </span>
      </div>

      {/* New Top-level Question Form */}
      {isAuthenticated ? (
        <form onSubmit={handleCreateComment} className="mb-8 space-y-3">
          <textarea
            rows={3}
            value={newCommentText}
            onChange={(e) => setNewCommentText(e.target.value)}
            placeholder="Ask a question or clarify a step in these notes..."
            className="w-full p-3.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-primary text-xs text-slate-800 placeholder:text-slate-400 font-sans"
          />
          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              size="sm"
              loading={submitting}
              disabled={!newCommentText.trim()}
            >
              Post Question
            </Button>
          </div>
        </form>
      ) : (
        <div className="mb-8 p-4 bg-slate-50 border border-slate-200 rounded-xl text-center text-xs text-slate-500">
          Sign in to post questions or replies to the Doubt Board.
        </div>
      )}

      {/* Comment Thread List */}
      {loading ? (
        <div className="space-y-4 py-4 animate-pulse">
          <div className="h-16 bg-slate-100 rounded-xl"></div>
          <div className="h-16 bg-slate-100 rounded-xl"></div>
        </div>
      ) : comments.length === 0 ? (
        <p className="text-xs text-slate-400 italic text-center py-6">
          No questions posted yet. Be the first to start a discussion!
        </p>
      ) : (
        <div className="space-y-6">
          {comments.map((comment) => (
            <div
              key={comment.id}
              className={`p-4 rounded-xl border transition-all ${
                comment.is_solved
                  ? 'bg-emerald-50/30 border-emerald-200/80'
                  : 'bg-slate-50/50 border-slate-200/80'
              }`}
            >
              {/* Header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 rounded-full bg-primary/10 text-primary font-bold text-xxs flex items-center justify-center">
                    {comment.user?.full_name?.charAt(0) || 'U'}
                  </div>
                  <span className="font-semibold text-xs text-slate-800">
                    {comment.user?.full_name || 'Student'}
                  </span>
                  <span className="text-xxs text-slate-400">
                    {new Date(comment.created_at).toLocaleDateString()}
                  </span>
                </div>

                {/* Solved marker / toggle */}
                <div className="flex items-center space-x-2">
                  {comment.is_solved && (
                    <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-xxs font-bold inline-flex items-center gap-1">
                      <span>✓</span> Solved
                    </span>
                  )}

                  {canToggleSolved(comment) && (
                    <button
                      type="button"
                      onClick={() =>
                        handleToggleSolved(comment.id, comment.is_solved)
                      }
                      className="text-xxs text-slate-500 hover:text-emerald-700 font-medium underline"
                    >
                      {comment.is_solved ? 'Mark Unsolved' : 'Mark as Solved'}
                    </button>
                  )}
                </div>
              </div>

              {/* Comment Content */}
              <p className="text-xs text-slate-700 whitespace-pre-wrap mb-3 leading-relaxed">
                {comment.content}
              </p>

              {/* Reply Action */}
              {isAuthenticated && replyingTo !== comment.id && (
                <button
                  type="button"
                  onClick={() => {
                    setReplyingTo(comment.id);
                    setReplyText('');
                  }}
                  className="text-xxs font-bold text-primary hover:text-primary-dark"
                >
                  ↳ Reply
                </button>
              )}

              {/* Reply Box */}
              {replyingTo === comment.id && (
                <div className="mt-3 pl-4 border-l-2 border-primary/30 space-y-2">
                  <textarea
                    rows={2}
                    value={replyText}
                    onChange={(e) => setReplyText(e.target.value)}
                    placeholder="Write a reply..."
                    className="w-full p-2.5 rounded-lg border border-slate-200 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <div className="flex justify-end space-x-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setReplyingTo(null)}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="button"
                      variant="primary"
                      size="sm"
                      loading={submitting}
                      onClick={() => handleCreateReply(comment.id)}
                    >
                      Post Reply
                    </Button>
                  </div>
                </div>
              )}

              {/* Nested Replies */}
              {comment.replies && comment.replies.length > 0 && (
                <div className="mt-3 pl-4 border-l-2 border-slate-200 space-y-2">
                  {comment.replies.map((reply) => (
                    <div
                      key={reply.id}
                      className="p-2.5 rounded-lg bg-white border border-slate-100 text-xs"
                    >
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-bold text-xxs text-slate-700">
                          {reply.user?.full_name || 'Student'}
                        </span>
                        <span className="text-xxs text-slate-400">
                          {new Date(reply.created_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-slate-600 text-xs whitespace-pre-wrap">
                        {reply.content}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
