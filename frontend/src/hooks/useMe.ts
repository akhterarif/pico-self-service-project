import { useQuery } from '@tanstack/react-query';
import { me } from '../api';

export const meQueryKey = ['me'] as const;

export function useMe() {
  return useQuery({ queryKey: meQueryKey, queryFn: me, retry: false });
}
