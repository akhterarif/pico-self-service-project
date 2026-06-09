import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { listAudit, listInvoices, listVms } from '../api';
import { ErrorBox, Spinner, StatusPill, Timeline } from '../components/common';

export function VmDetailsPage() {
  const { id } = useParams();
  const vms = useQuery({ queryKey: ['vms'], queryFn: listVms });
  const invoices = useQuery({ queryKey: ['invoices'], queryFn: listInvoices });
  const audit = useQuery({ queryKey: ['audit'], queryFn: listAudit });

  if (vms.isLoading || invoices.isLoading || audit.isLoading) return <Spinner />;
  if (vms.isError || invoices.isError || audit.isError) return <ErrorBox />;

  const vm = vms.data?.find((item) => String(item.id) === id);
  if (!vm) return <ErrorBox message="VM not found." />;

  const invoice = invoices.data?.find((item) => item.vm === vm.id);
  const events = audit.data?.filter((item) => item.entity_type === 'vm' && item.entity_id === String(vm.id));

  return (
    <section className="grid gap-4 lg:grid-cols-[1fr_360px]">
      <div className="border border-line bg-white p-5">
        <h2 className="text-xl font-semibold">{vm.name}</h2>
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
          <dt>Package</dt>
          <dd>{vm.package.name}</dd>
          <dt>Status</dt>
          <dd>
            <StatusPill value={vm.status} />
          </dd>
          <dt>IP</dt>
          <dd>{vm.ip_address || '-'}</dd>
          <dt>Created</dt>
          <dd>{new Date(vm.created_at).toLocaleString()}</dd>
          <dt>Invoice</dt>
          <dd>{invoice ? `${invoice.invoice_number} (${invoice.status})` : '-'}</dd>
        </dl>
      </div>
      <Timeline logs={events || []} />
    </section>
  );
}
