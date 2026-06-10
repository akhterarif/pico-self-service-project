import axios from 'axios';

export type User = { id: number; email: string; role: 'CUSTOMER' | 'ADMIN'; company_name?: string };
export type Package = { id: number; name: string; slug: string; vcpu: number; ram_mb: number; disk_gb: number; monthly_price: string; is_active: boolean };
export type Vm = { id: number; name: string; package: Package; cloud_server_id: string; status: string; ip_address?: string; created_at: string; updated_at: string; latest_invoice_id?: number, usage?: { storage: number; cpu: number; memory: number; network: number } };
export type Invoice = { id: number; invoice_number: string; vm: number; vm_name: string; amount: string; currency: string; status: string; due_date: string; created_at: string; paid_at?: string };
export type AuditLog = { id: number; entity_type: string; entity_id: string; action: string; description: string; metadata: Record<string, unknown>; created_at: string };
export type Customer = { id: number; email: string; company_name: string; created_at: string };

const baseURL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';
export const api = axios.create({ baseURL });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const login = async (email: string, password: string) => (await api.post('/auth/login', { email, password })).data;
export const register = async (email: string, password: string, company_name: string) => (await api.post('/auth/register', { email, password, company_name })).data;
export const me = async () => (await api.get<User>('/auth/me')).data;
export const listPackages = async () => (await api.get<Package[]>('/packages/')).data;
export const listVms = async () => (await api.get<Vm[]>('/vms/')).data;
export const createVm = async (payload: { name: string; package_id: number }) => (await api.post<Vm>('/vms/', payload)).data;
export const vmAction = async (id: number, action: 'start' | 'stop') => (await api.post<Vm>(`/vms/${id}/${action}/`)).data;
export const deleteVm = async (id: number) => (await api.delete(`/vms/${id}/`)).data;
export const listVmAudit = async (id: number) => (await api.get<AuditLog[]>(`/vms/${id}/audit/`)).data;
export const listVmInvoice = async (id: number) => (await api.get<Invoice[]>(`/vms/${id}/invoice/`)).data;
export const listInvoices = async () => (await api.get<Invoice[]>('/invoices/')).data;
export const payInvoice = async (id: number) => (await api.post<Invoice>(`/invoices/${id}/pay/`)).data;
export const listAudit = async () => (await api.get<AuditLog[]>('/audit/')).data;
export const customerDashboard = async () => (await api.get('/dashboard/')).data;
export const adminDashboard = async () => (await api.get('/admin/dashboard/')).data;
export const listCustomers = async () => (await api.get<Customer[]>('/admin/customers/')).data;
export const aiChat = async (prompt: string) => (await api.post('/ai/chat/', { prompt })).data;
export const aiQuery = async (text: string) => (await api.post('/ai/query/', { text })).data;
