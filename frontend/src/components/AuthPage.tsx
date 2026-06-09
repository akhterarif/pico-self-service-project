import React from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { login, register } from '../api';
import { ErrorBox } from './common';

export function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (form: FormData) => {
      const email = String(form.get('email'));
      const password = String(form.get('password'));

      if (mode === 'login') {
        return login(email, password);
      }

      const company = String(form.get('company'));
      return register(email, password, company);
    },
    onSuccess: async (data, variables) => {
      const form = variables as FormData;
      const email = String(form.get('email'));
      const password = String(form.get('password'));

      if (data?.access) {
        localStorage.setItem('accessToken', data.access);
      } else if (mode === 'register') {
        const tokens = await login(email, password);
        localStorage.setItem('accessToken', tokens.access);
      }

      await queryClient.invalidateQueries({ queryKey: ['me'] });
      navigate('/');
    },
  });

  return (
    <main className="grid min-h-screen place-items-center bg-[#edf2f5] px-4">
      <section className="w-full max-w-md border border-line bg-white p-8 shadow-sm">
        <h1 className="text-2xl font-semibold">PICO Self-Service Cloud Portal</h1>
        <p className="mt-2 text-sm text-slate-600">
          {mode === 'login' ? 'Sign in to manage cloud resources.' : 'Create a customer account.'}
        </p>
        <form
          className="mt-6 space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            mutation.mutate(new FormData(event.currentTarget));
          }}
        >
          <input id="email" name="email" type="email" required placeholder="Email" className="focus-ring w-full border border-line px-3 py-2" />
          {mode === 'register' && <input name="company" required placeholder="Company name" className="focus-ring w-full border border-line px-3 py-2" />}
          <input id="password" name="password" type="password" required placeholder="Password" className="focus-ring w-full border border-line px-3 py-2" />
          {mutation.isError && <ErrorBox message="Authentication failed. Check the details and try again." />}
          <button className="focus-ring w-full bg-brand px-4 py-2 font-semibold text-white" disabled={mutation.isPending}>
            {mutation.isPending ? 'Working...' : mode === 'login' ? 'Login' : 'Register'}
          </button>
        </form>
        <Link className="mt-4 block text-sm text-brand" to={mode === 'login' ? '/register' : '/login'}>
          {mode === 'login' ? 'Create an account' : 'Already have an account'}
        </Link>
      </section>
    </main>
  );
}
