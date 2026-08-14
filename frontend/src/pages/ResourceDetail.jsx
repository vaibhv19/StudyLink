import React from 'react';
import { useParams } from 'react-router-dom';

export default function ResourceDetail() {
  const { id } = useParams();
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-black text-slate-900">Resource Detail</h1>
      <p className="text-slate-600">Resource ID: {id}</p>
    </div>
  );
}
