import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 font-medium">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-slate-800 text-sm">
            StudyLink
          </span>
          <span>&copy; {new Date().getFullYear()} Digital Campus Platform</span>
        </div>
        <div className="flex space-x-6 text-slate-500">
          <Link to="/vault" className="hover:text-primary transition-colors">Resource Vault</Link>
          <Link to="/market" className="hover:text-primary transition-colors">Marketplace</Link>
          <Link to="/auth" className="hover:text-primary transition-colors">Authentication</Link>
        </div>
      </div>
    </footer>
  );
}
