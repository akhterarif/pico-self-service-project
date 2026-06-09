import React from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { deleteVm, listVms, vmAction } from '../api';
import { Empty, Spinner, StatusPill, Table } from '../components/common';
import { Play, Square, Trash2 } from 'lucide-react';

export function ResourcesPage() {
  const query = useQuery({ queryKey: ['vms'], queryFn: listVms });
  const queryClient = useQueryClient();
  const action = useMutation({
    mutationFn: ({ id, action }: { id: number; action: 'start' | 'stop' }) => vmAction(id, action),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['vms'] }),
  });
  const remove = useMutation({
    mutationFn: deleteVm,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['vms'] }),
  });

  if (query.isLoading) return <Spinner />;
  if (!query.data?.length) return <Empty title="No virtual machines yet." />;

  return (
    <Table headers={['Name', 'Package', 'Status', 'IP', 'Actions']}>
      {query.data.map((vm) => (
        <tr key={vm.id}>
          <td>
            <Link className="text-brand" to={`/resources/${vm.id}`}>
              {vm.name}
            </Link>
          </td>
          <td>{vm.package.name}</td>
          <td>
            <StatusPill value={vm.status} />
          </td>
          <td>{vm.ip_address || '-'}</td>
          <td className="flex gap-2">
            <button title="Start" onClick={() => action.mutate({ id: vm.id, action: 'start' })}>
              <Play size={16} />
            </button>
            <button title="Stop" onClick={() => action.mutate({ id: vm.id, action: 'stop' })}>
              <Square size={16} />
            </button>
            <button title="Delete" onClick={() => remove.mutate(vm.id)}>
              <Trash2 size={16} />
            </button>
          </td>
        </tr>
      ))}
    </Table>
  );
}
