import React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createVm, listPackages } from '../api';
import { Money, Spinner } from '../components/common';

export function CatalogPage() {
  const query = useQuery({ queryKey: ['packages'], queryFn: listPackages });
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: createVm,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['vms'] }),
  });

  if (query.isLoading) return <Spinner />;

  return (
    <section>
      <h2 className="mb-4 text-xl font-semibold">Catalog</h2>
      {mutation.isSuccess && <div className="mb-4 border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800">VM provisioning requested.</div>}
      <div className="grid gap-4 lg:grid-cols-3">
        {query.data?.map((pkg) => (
          <div key={pkg.id} className="border border-line bg-white p-5">
            <h3 className="text-lg font-semibold">{pkg.name}</h3>
            <div className="mt-3 text-sm text-slate-600">
              {pkg.vcpu} vCPU · {pkg.ram_mb / 1024} GB RAM · {pkg.disk_gb} GB disk
            </div>
            <div className="mt-4 text-2xl font-semibold">
              <Money value={pkg.monthly_price} />
              <span className="text-sm font-normal text-slate-500"> / month</span>
            </div>
            <form
              className="mt-4 flex gap-2"
              onSubmit={(event) => {
                event.preventDefault();
                const form = new FormData(event.currentTarget);
                const name = String(form.get('name'));
                mutation.mutate({ name, package_id: pkg.id });
              }}
            >
              <input name="name" required placeholder="vm-name" className="focus-ring min-w-0 flex-1 border border-line px-3 py-2 text-sm" />
              <button className="focus-ring bg-brand px-3 py-2 text-sm font-semibold text-white">Provision</button>
            </form>
          </div>
        ))}
      </div>
    </section>
  );
}
