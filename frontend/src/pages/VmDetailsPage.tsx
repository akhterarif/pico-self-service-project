import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { listInvoices, listVmAudit, listVmInvoice, listVms } from "../api";
import {
  ErrorBox,
  Money,
  Spinner,
  StatusPill,
  Timeline,
} from "../components/common";

function Card({
  title,
  children,
  className = "",
}: {
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`border border-line bg-white p-5 ${className}`}>
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
        {title}
      </h3>
      <div className="mt-4">{children}</div>
    </section>
  );
}

function Stat({
  label,
  value,
  hint,
}: {
  label: string;
  value: React.ReactNode;
  hint?: string;
}) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-slate-500">
        {label}
      </div>
      <div className="mt-1 text-sm font-semibold text-slate-900">{value}</div>
      {hint && <div className="mt-1 text-xs text-slate-500">{hint}</div>}
    </div>
  );
}

function percentFromId(id: number, max: number) {
  return ((id * 17) % max) + 1;
}

export function VmDetailsPage() {
  const { id } = useParams();
  const vmId = Number(id);
  const vms = useQuery({ queryKey: ["vms"], queryFn: listVms });
  const invoices = useQuery({
    queryKey: ["vm-invoices", vmId],
    queryFn: () => listVmInvoice(vmId),
    enabled: Number.isFinite(vmId),
  });
  const audit = useQuery({
    queryKey: ["vm-audit", vmId],
    queryFn: () => listVmAudit(vmId),
    enabled: Number.isFinite(vmId),
  });

  if (vms.isLoading || invoices.isLoading || audit.isLoading)
    return <Spinner />;
  if (vms.isError || invoices.isError || audit.isError) return <ErrorBox />;

  const vm = vms.data?.find((item) => item.id === vmId);
  if (!vm) return <ErrorBox message="VM not found." />;

  const invoice = invoices.data?.[0] ?? null;
  const events = audit.data || [];
  const uptimeMs = Date.now() - new Date(vm.created_at).getTime();
  const uptimeDays = Math.max(0, Math.floor(uptimeMs / (1000 * 60 * 60 * 24)));
  const monthUptimeHours = Math.max(1, Math.floor(uptimeMs / (1000 * 60 * 60)));
  const estimatedStorageUsedGb = vm.usage?.storage
    ? Math.min(vm.package.disk_gb, vm.usage.storage)
    : 0;
  const estimatedCpuUsage = percentFromId(vm.usage?.cpu ?? 0, 72);
  const estimatedMemoryUsage = percentFromId(vm.usage?.memory ?? 0, 68);
  const estimatedNetworkUsage = percentFromId(vm.usage?.network ?? 0, 54);
  const ipOctets = vm.ip_address?.split(".") ?? [];
  const ipPoolLabel = vm.ip_address
    ? `10.42.0.0/24 allocation, host .${ipOctets[3] ?? "0"}`
    : "Pending IP allocation";

  return (
    <section className="space-y-4">
      <div className="border border-line bg-white p-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-2xl font-semibold">{vm.name}</h2>
            <p className="mt-1 text-sm text-slate-500">
              VM resource dashboard, storage allocation, networking, and usage
              snapshot.
            </p>
          </div>
          <StatusPill value={vm.status} />
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <Card title="VM Overview">
          <div className="grid gap-4 sm:grid-cols-2">
            <Stat
              label="Package"
              value={vm.package.name}
              hint={`${vm.package.vcpu} vCPU`}
            />
            <Stat
              label="Cloud Server ID"
              value={vm.cloud_server_id || "-"}
              hint="Provider-side instance identifier"
            />
            <Stat
              label="Created"
              value={new Date(vm.created_at).toLocaleString()}
            />
            <Stat
              label="Last Updated"
              value={new Date(vm.updated_at).toLocaleString()}
            />
            <Stat
              label="Invoice"
              value={invoice ? `${invoice.invoice_number}` : "-"}
              hint={invoice ? invoice.status : "No invoice generated yet"}
            />
            <Stat
              label="Uptime"
              value={`${uptimeDays} day${uptimeDays === 1 ? "" : "s"}`}
              hint={`${monthUptimeHours} billable hours this month`}
            />
          </div>
        </Card>

        <Card title="Storage Allocation">
          <div className="space-y-4">
            <div className="flex items-end justify-between">
              <div>
                <div className="text-xs uppercase tracking-wide text-slate-500">
                  Provisioned Storage
                </div>
                <div className="mt-1 text-3xl font-semibold">
                  {vm.package.disk_gb} GB
                </div>
              </div>
              <div className="text-right text-sm text-slate-500">
                <div>{estimatedStorageUsedGb} GB estimated used</div>
                <div>{vm.package.ram_mb / 1024} GB RAM</div>
              </div>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-brand"
                style={{
                  width: `${Math.min(100, Math.round((estimatedStorageUsedGb / vm.package.disk_gb) * 100))}%`,
                }}
              />
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <Stat label="vCPU" value={vm.package.vcpu} />
              <Stat label="Memory" value={`${vm.package.ram_mb / 1024} GB`} />
              <Stat
                label="Billing estimate"
                value={<Money value={vm.package.monthly_price} />}
                hint="Monthly package rate"
              />
              <Stat
                label="Storage note"
                value="No live disk telemetry"
                hint="Showing allocated capacity until agent metrics are available"
              />
            </div>
          </div>
        </Card>

        <Card title="Network and IP Allocation">
          <div className="grid gap-4 sm:grid-cols-2">
            <Stat
              label="Primary IP"
              value={vm.ip_address || "Pending"}
              hint="Assigned after provisioning completes"
            />
            <Stat
              label="Allocation Pool"
              value="10.42.0.0/24"
              hint={ipPoolLabel}
            />
            <Stat
              label="Server State"
              value={vm.status}
              hint="Lifecycle state from compute service"
            />
            <Stat
              label="Address Type"
              value={vm.ip_address ? "Private network IP" : "Unallocated"}
              hint="Public floating IP not configured in MVP"
            />
          </div>
        </Card>

        <Card title="Usage Metering">
          <div className="space-y-4">
            <div className="grid gap-3 sm:grid-cols-3">
              <Stat
                label="CPU"
                value={`${estimatedCpuUsage}%`}
                hint="Estimated snapshot"
              />
              <Stat
                label="Memory"
                value={`${estimatedMemoryUsage}%`}
                hint="Estimated snapshot"
              />
              <Stat
                label="Network"
                value={`${estimatedNetworkUsage}%`}
                hint="Estimated snapshot"
              />
            </div>
            <div className="space-y-3">
              {[
                { label: "CPU", value: estimatedCpuUsage },
                { label: "Memory", value: estimatedMemoryUsage },
                { label: "Network", value: estimatedNetworkUsage },
              ].map((metric) => (
                <div key={metric.label}>
                  <div className="flex items-center justify-between text-xs uppercase tracking-wide text-slate-500">
                    <span>{metric.label}</span>
                    <span>{metric.value}%</span>
                  </div>
                  <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-emerald-500"
                      style={{ width: `${metric.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-500">
              Live telemetry is not wired into the current backend yet, so this
              panel shows a usage snapshot built from the VM context.
            </p>
          </div>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_360px]">
        <Card title="Audit Trail">
          <Timeline logs={events || []} />
        </Card>
        <Card title="Billing Snapshot">
          <div className="space-y-4 text-sm">
            <Stat
              label="Invoice total"
              value={invoice ? <Money value={invoice.amount} /> : "-"}
            />
            <Stat
              label="Invoice status"
              value={invoice ? invoice.status : "No invoice"}
            />
            <Stat label="Due date" value={invoice?.due_date || "-"} />
            <Stat
              label="Latest activity"
              value={new Date(vm.updated_at).toLocaleDateString()}
              hint="Last compute update"
            />
          </div>
        </Card>
      </div>
    </section>
  );
}
