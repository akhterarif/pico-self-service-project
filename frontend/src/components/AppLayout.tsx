import React from 'react';
import { Link, Navigate, Outlet, useNavigate } from 'react-router-dom';
import {
  Activity,
  CreditCard,
  LayoutDashboard,
  LogOut,
  PackageOpen,
  Server,
  Shield,
  UserCircle,
  type LucideIcon,
} from 'lucide-react';
import { useMe } from '../hooks/useMe';
import { Spinner } from './common';

type NavItem = readonly [string, string, LucideIcon];

export function RequireAnon({ children }: { children: React.ReactNode }) {
  return localStorage.getItem('accessToken') ? <Navigate to="/" replace /> : <>{children}</>;
}

export function AppLayout() {
  const { data: user, isLoading, isError } = useMe();
  const navigate = useNavigate();

  if (isLoading) return <Spinner />;
  if (isError || !user) return <Navigate to="/login" replace />;

  const items: NavItem[] =
    user.role === 'ADMIN'
      ? [
          ['/admin', 'Dashboard', Shield],
          ['/admin/customers', 'Customers', UserCircle],
          ['/admin/resources', 'Resources', Server],
          ['/admin/invoices', 'Invoices', CreditCard],
        ]
      : [
          ['/', 'Dashboard', LayoutDashboard],
          ['/catalog', 'Catalog', PackageOpen],
          ['/resources', 'Resources', Server],
          ['/invoices', 'Invoices', CreditCard],
          ['/audit', 'Audit', Activity],
          ['/profile', 'Profile', UserCircle],
        ];

  return (
    <div className="min-h-screen bg-[#f6f8fa]">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-line bg-white p-4 md:block">
        <div className="mb-6 text-lg font-semibold">PICO Portal</div>
        <nav className="space-y-1">
          {items.map(([to, label, Icon]) => (
            <Link key={to} to={to} className="flex items-center gap-3 px-3 py-2 text-sm hover:bg-slate-100">
              <Icon size={18} />
              {label}
            </Link>
          ))}
        </nav>
      </aside>
      <header className="border-b border-line bg-white p-4 md:ml-64">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-semibold">{user.company_name || user.email}</div>
            <div className="text-xs text-slate-500">{user.role}</div>
          </div>
          <button
            className="focus-ring flex items-center gap-2 border border-line px-3 py-2 text-sm"
            onClick={() => {
              localStorage.removeItem('accessToken');
              navigate('/login');
            }}
          >
            <LogOut size={16} />
            Logout
          </button>
        </div>
      </header>
      <main className="p-4 md:ml-64 md:p-6">
        <Outlet />
      </main>
    </div>
  );
}
