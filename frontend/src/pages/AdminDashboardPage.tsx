import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminDashboard } from '../api';
import { DashboardGrid, Spinner } from '../components/common';

export function AdminDashboardPage() {
  const query = useQuery({ queryKey: ['admin-dashboard'], queryFn: adminDashboard });

  if (query.isLoading) return <Spinner />;

  return <DashboardGrid data={query.data} className="sm:grid-cols-2 lg:grid-cols-5" />;
}
