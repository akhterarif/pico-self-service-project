import '@testing-library/jest-dom/vitest';
import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

test('renders login page', () => {
  localStorage.removeItem('accessToken');
  render(<QueryClientProvider client={new QueryClient()}><MemoryRouter initialEntries={["/login"]}><App /></MemoryRouter></QueryClientProvider>);
  expect(screen.getByText('PICO Self-Service Cloud Portal')).toBeInTheDocument();
});
