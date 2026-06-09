import React from 'react';
import { Route, Routes } from 'react-router-dom';
import { AppLayout, RequireAnon } from './components/AppLayout';
import { AuthPage } from './components/AuthPage';
import { DashboardPage } from './pages/DashboardPage';
import { CatalogPage } from './pages/CatalogPage';
import { ResourcesPage } from './pages/ResourcesPage';
import { VmDetailsPage } from './pages/VmDetailsPage';
import { InvoicesPage } from './pages/InvoicesPage';
import { AuditPage } from './pages/AuditPage';
import { ProfilePage } from './pages/ProfilePage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { CustomersPage } from './pages/CustomersPage';
import { AdminResourcesPage } from './pages/AdminResourcesPage';
import { AdminInvoicesPage } from './pages/AdminInvoicesPage';

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={
          <RequireAnon>
            <AuthPage mode="login" />
          </RequireAnon>
        }
      />
      <Route
        path="/register"
        element={
          <RequireAnon>
            <AuthPage mode="register" />
          </RequireAnon>
        }
      />
      <Route element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route path="catalog" element={<CatalogPage />} />
        <Route path="resources" element={<ResourcesPage />} />
        <Route path="resources/:id" element={<VmDetailsPage />} />
        <Route path="invoices" element={<InvoicesPage />} />
        <Route path="audit" element={<AuditPage />} />
        <Route path="profile" element={<ProfilePage />} />
        <Route path="admin" element={<AdminDashboardPage />} />
        <Route path="admin/customers" element={<CustomersPage />} />
        <Route path="admin/resources" element={<AdminResourcesPage />} />
        <Route path="admin/invoices" element={<AdminInvoicesPage />} />
      </Route>
    </Routes>
  );
}
