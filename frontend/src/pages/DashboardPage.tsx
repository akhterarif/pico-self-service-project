import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { customerDashboard } from '../api';
import { DashboardGrid, ErrorBox, Spinner } from '../components/common';

export function DashboardPage() {
  const query = useQuery({ queryKey: ['dashboard'], queryFn: customerDashboard });

  if (query.isLoading) return <Spinner />;
  if (query.isError) return <ErrorBox />;

  return (
    <section>
      <h2 className="mb-4 text-xl font-semibold">Dashboard</h2>
      <DashboardGrid data={query.data} />
    </section>
  );
}
