import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { listAudit } from '../api';
import { Spinner, Timeline } from '../components/common';

export function AuditPage() {
  const query = useQuery({ queryKey: ['audit'], queryFn: listAudit });

  if (query.isLoading) return <Spinner />;

  return <Timeline logs={query.data || []} />;
}
