import React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { payInvoice, listInvoices } from '../api';
import { Empty, Money, Spinner, StatusPill, Table } from '../components/common';

export function InvoicesPage() {
  const query = useQuery({ queryKey: ['invoices'], queryFn: listInvoices });
  const queryClient = useQueryClient();
  const pay = useMutation({
    mutationFn: payInvoice,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['invoices'] }),
  });

  if (query.isLoading) return <Spinner />;
  if (!query.data?.length) return <Empty title="No invoices yet." />;

  return (
    <Table headers={['Number', 'VM', 'Amount', 'Due', 'Status', 'Action']}>
      {query.data.map((invoice) => (
        <tr key={invoice.id}>
          <td>{invoice.invoice_number}</td>
          <td>{invoice.vm_name}</td>
          <td>
            <Money value={invoice.amount} />
          </td>
          <td>{invoice.due_date}</td>
          <td>
            <StatusPill value={invoice.status} />
          </td>
          <td>{invoice.status !== 'PAID' && <button className="bg-brand px-3 py-1 text-sm text-white" onClick={() => pay.mutate(invoice.id)}>Pay</button>}</td>
        </tr>
      ))}
    </Table>
  );
}
