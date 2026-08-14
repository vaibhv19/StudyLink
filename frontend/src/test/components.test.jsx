import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Badge from '../components/Badge';
import UpvoteButton from '../components/UpvoteButton';
import Button from '../components/Button';
import RagChatPanel from '../components/RagChatPanel';
import DoubtBoard from '../components/DoubtBoard';
import { useAuthStore } from '../store/authStore';
import { apiClient } from '../hooks/useApi';

vi.mock('../hooks/useApi', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    interceptors: {
      request: { use: vi.fn(), handlers: [] },
      response: { use: vi.fn(), handlers: [] },
    },
  },
  default: () => ({
    get: vi.fn(),
    post: vi.fn(),
  }),
}));

describe('UI Components Unit & Integration Tests', () => {
  describe('Badge component', () => {
    it('renders READY status badge with green styling', () => {
      render(<Badge status="READY" />);
      const badge = screen.getByText('READY');
      expect(badge).toBeInTheDocument();
      expect(badge.className).toContain('text-emerald-700');
    });

    it('renders PROCESSING status badge with animate-pulse', () => {
      render(<Badge status="PROCESSING" />);
      const badge = screen.getByText('PROCESSING');
      expect(badge).toBeInTheDocument();
      expect(badge.className).toContain('animate-pulse');
    });

    it('renders Marketplace AVAILABLE badge', () => {
      render(<Badge status="AVAILABLE" />);
      expect(screen.getByText('AVAILABLE')).toBeInTheDocument();
    });

    it('renders Marketplace REQUESTED badge', () => {
      render(<Badge status="REQUESTED" />);
      const badge = screen.getByText('REQUESTED');
      expect(badge.className).toContain('bg-amber-500');
    });
  });

  describe('UpvoteButton component', () => {
    it('renders pill shape with count', () => {
      render(<UpvoteButton count={42} hasUpvoted={false} />);
      expect(screen.getByText('42')).toBeInTheDocument();
    });

    it('applies accent style when hasUpvoted is true', () => {
      render(<UpvoteButton count={15} hasUpvoted={true} />);
      const btn = screen.getByRole('button');
      expect(btn.className).toContain('text-accent');
    });

    it('calls onToggle callback when clicked', () => {
      const handleToggle = vi.fn();
      render(<UpvoteButton count={10} onToggle={handleToggle} />);
      fireEvent.click(screen.getByRole('button'));
      expect(handleToggle).toHaveBeenCalledTimes(1);
    });
  });

  describe('Button component', () => {
    it('renders button with primary variant styling', () => {
      render(<Button variant="primary">Click Me</Button>);
      const btn = screen.getByRole('button', { name: /Click Me/i });
      expect(btn).toBeInTheDocument();
      expect(btn.className).toContain('bg-primary');
    });

    it('renders spinner when loading is true', () => {
      render(<Button loading={true}>Submit</Button>);
      const btn = screen.getByRole('button');
      expect(btn).toBeDisabled();
    });
  });

  describe('RagChatPanel component', () => {
    it('shows warning and disables chat when status is PROCESSING', () => {
      render(
        <RagChatPanel
          resourceId="res-1"
          resourceStatus="PROCESSING"
        />
      );

      expect(
        screen.getByText(/Embedding Ingestion in Progress/i)
      ).toBeInTheDocument();
      const input = screen.getByPlaceholderText(
        /Chat unavailable until document is READY/i
      );
      expect(input).toBeDisabled();
    });

    it('enables input and handles query response with citations', async () => {
      useAuthStore.getState().login({ id: 'u1', email: 'test@example.com' }, 'token-123');

      apiClient.post.mockResolvedValueOnce({
        data: {
          answer: 'Complexity is explained as O(n) linear growth.',
          sources: [
            {
              page_number: 4,
              excerpt: 'linear growth relative to input size',
              similarity_score: 0.89,
            },
          ],
        },
      });

      const onCitationClick = vi.fn();

      render(
        <RagChatPanel
          resourceId="res-123"
          resourceStatus="READY"
          onCitationClick={onCitationClick}
        />
      );

      const input = screen.getByPlaceholderText(/Ask about concepts/i);
      expect(input).not.toBeDisabled();

      fireEvent.change(input, { target: { value: 'Explain complexity' } });
      fireEvent.submit(screen.getByRole('button', { name: /Send/i }));

      await waitFor(() => {
        expect(
          screen.getByText(/Complexity is explained as O\(n\) linear growth./i)
        ).toBeInTheDocument();
      });

      // Verify citation card
      expect(screen.getByText(/Page 4/i)).toBeInTheDocument();
      expect(screen.getByText(/89% match/i)).toBeInTheDocument();

      // Click citation
      fireEvent.click(screen.getByText(/Page 4/i));
      expect(onCitationClick).toHaveBeenCalledWith(4);
    });
  });

  describe('DoubtBoard component', () => {
    it('fetches and renders threaded comments', async () => {
      apiClient.get.mockResolvedValueOnce({
        data: [
          {
            id: 1,
            content: 'How is step 3 derived?',
            is_solved: false,
            created_at: '2026-08-14T10:00:00Z',
            user: { full_name: 'Bob' },
            replies: [
              {
                id: 2,
                content: 'Use integration by parts.',
                created_at: '2026-08-14T10:05:00Z',
                user: { full_name: 'Alice' },
              },
            ],
          },
        ],
      });

      render(<DoubtBoard resourceId="res-10" resourceUploaderId="u-uploader" />);

      await waitFor(() => {
        expect(screen.getByText('How is step 3 derived?')).toBeInTheDocument();
        expect(screen.getByText('Use integration by parts.')).toBeInTheDocument();
      });
    });
  });
});
