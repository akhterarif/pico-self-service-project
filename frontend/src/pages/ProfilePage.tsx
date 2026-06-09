import React from 'react';
import { ErrorBox, Spinner } from '../components/common';
import { useMe } from '../hooks/useMe';

export function ProfilePage() {
  const query = useMe();

  if (query.isLoading) return <Spinner />;
  if (query.isError || !query.data) return <ErrorBox />;

  return (
    <section className="border border-line bg-white p-5">
      <h2 className="text-xl font-semibold">Profile</h2>
      <p className="mt-4 text-sm">{query.data.email}</p>
      <p className="text-sm text-slate-600">{query.data.company_name}</p>
    </section>
  );
}
