import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { listCustomers } from '../api';
import { Spinner, Table } from '../components/common';

export function CustomersPage() {
  const query = useQuery({ queryKey: ['customers'], queryFn: listCustomers });

  if (query.isLoading) return <Spinner />;

  return (
    <Table headers={['Company', 'Email', 'Created']}>
      {query.data?.map((customer) => (
        <tr key={customer.id}>
          <td>{customer.company_name}</td>
          <td>{customer.email}</td>
          <td>{new Date(customer.created_at).toLocaleDateString()}</td>
        </tr>
      ))}
    </Table>
  );
}
