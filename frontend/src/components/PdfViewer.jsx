import React, { useState, useEffect } from 'react';

export default function PdfViewer({ url, targetPage = 1, onPageChange }) {
  const [currentPage, setCurrentPage] = useState(targetPage);
  const [scale, setScale] = useState(100);

  useEffect(() => {
    if (targetPage && targetPage !== currentPage) {
      setCurrentPage(targetPage);
    }
  }, [targetPage]);

  const handlePageChange = (newPage) => {
    if (newPage < 1) return;
    setCurrentPage(newPage);
    if (onPageChange) onPageChange(newPage);
  };

  if (!url) {
    return (
      <div className="h-full min-h-[500px] flex items-center justify-center bg-slate-100/70 rounded-2xl border border-slate-200 text-slate-400 text-sm">
        No document URL provided.
      </div>
    );
  }

  // Append page hash for standard browser PDF viewer iframe
  const pdfViewerSrc = `${url}#page=${currentPage}&zoom=${scale}`;

  return (
    <div className="flex flex-col h-full bg-slate-900 rounded-2xl overflow-hidden border border-slate-800 shadow-xl min-h-[600px] lg:min-h-[720px]">
      {/* Viewer Toolbar */}
      <div className="bg-slate-950/90 backdrop-blur-md px-4 py-2.5 flex items-center justify-between text-slate-300 text-xs border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <span className="font-mono text-slate-400">PAGE</span>
          <div className="flex items-center space-x-1 bg-slate-900 px-2 py-1 rounded-lg border border-slate-800">
            <button
              type="button"
              disabled={currentPage <= 1}
              onClick={() => handlePageChange(currentPage - 1)}
              className="px-1.5 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
              title="Previous Page"
            >
              ◀
            </button>
            <input
              type="number"
              min="1"
              value={currentPage}
              onChange={(e) => handlePageChange(parseInt(e.target.value, 10) || 1)}
              className="w-10 bg-transparent text-center text-white font-mono text-xs focus:outline-none"
            />
            <button
              type="button"
              onClick={() => handlePageChange(currentPage + 1)}
              className="px-1.5 hover:text-white"
              title="Next Page"
            >
              ▶
            </button>
          </div>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => setScale((s) => Math.max(50, s - 10))}
            className="p-1 hover:text-white bg-slate-900 rounded border border-slate-800"
            title="Zoom Out"
          >
            🔍 -
          </button>
          <span className="font-mono w-10 text-center">{scale}%</span>
          <button
            type="button"
            onClick={() => setScale((s) => Math.min(200, s + 10))}
            className="p-1 hover:text-white bg-slate-900 rounded border border-slate-800"
            title="Zoom In"
          >
            🔍 +
          </button>

          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="ml-3 px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition-colors inline-flex items-center gap-1"
          >
            <span>Open</span>
            <span>↗</span>
          </a>
        </div>
      </div>

      {/* Embedded Document Frame */}
      <div className="flex-grow relative bg-slate-900">
        <iframe
          key={`${url}-page-${currentPage}-scale-${scale}`}
          src={pdfViewerSrc}
          title="PDF Document Viewer"
          className="w-full h-full border-0 absolute inset-0"
        />
      </div>
    </div>
  );
}
