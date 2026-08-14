import React from 'react';
import { useParams } from 'react-router-dom';

export default function ListingDetail() {
  const { id } = useParams();
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-black text-slate-900">Listing Detail</h1>
      <p className="text-slate-600">Listing ID: {id}</p>
    </div>
  );
}
