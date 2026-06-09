import React from 'react';

export function StatusPill({ value }: { value: string }) {
  const tone =
    value === 'ACTIVE' || value === 'PAID'
      ? 'bg-emerald-100 text-emerald-800'
      : value === 'PENDING' || value === 'PROVISIONING'
        ? 'bg-amber-100 text-amber-800'
        : 'bg-slate-100 text-slate-700';

  return <span className={`rounded px-2 py-1 text-xs font-semibold ${tone}`}>{value}</span>;
}

export function Money({ value }: { value: string }) {
  return <span>${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>;
}

export function Empty({ title }: { title: string }) {
  return <div className="border border-dashed border-line bg-white p-8 text-center text-sm text-slate-500">{title}</div>;
}

export function Spinner() {
  return <div className="p-6 text-sm text-slate-500">Loading...</div>;
}

export function ErrorBox({ message = 'Something went wrong.' }: { message?: string }) {
  return <div className="border border-red-200 bg-red-50 p-4 text-sm text-red-700">{message}</div>;
}

export function Table({ headers, children }: { headers: string[]; children: React.ReactNode }) {
  return (
    <div className="overflow-x-auto border border-line bg-white">
      <table className="w-full min-w-[720px] text-left text-sm">
        <thead className="bg-slate-100 text-slate-600">
          <tr>
            {headers.map((header) => (
              <th key={header} className="px-4 py-3 font-semibold">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-line [&_td]:px-4 [&_td]:py-3">{children}</tbody>
      </table>
    </div>
  );
}

export function DashboardGrid({
  data,
  className = 'sm:grid-cols-2 lg:grid-cols-4',
}: {
  data: Record<string, unknown>;
  className?: string;
}) {
  return (
    <div className={`grid gap-4 ${className}`}>
      {Object.entries(data).map(([key, value]) => (
        <div className="border border-line bg-white p-4" key={key}>
          <div className="text-xs text-slate-500">{key.replaceAll('_', ' ')}</div>
          <div className="mt-2 text-2xl font-semibold">{String(value)}</div>
        </div>
      ))}
    </div>
  );
}

export type TimelineLog = {
  id: number;
  action: string;
  description: string;
  created_at: string;
};

export function Timeline({ logs }: { logs: TimelineLog[] }) {
  if (!logs.length) return <Empty title="No audit events." />;

  return (
    <div className="border border-line bg-white p-5">
      <h3 className="mb-4 font-semibold">Audit Timeline</h3>
      <ol className="space-y-4">
        {logs.map((log) => (
          <li key={log.id} className="border-l-2 border-brand pl-3">
            <div className="text-sm font-semibold">{log.action.replaceAll('_', ' ')}</div>
            <div className="text-sm text-slate-600">{log.description}</div>
            <div className="text-xs text-slate-400">{new Date(log.created_at).toLocaleString()}</div>
          </li>
        ))}
      </ol>
    </div>
  );
}
