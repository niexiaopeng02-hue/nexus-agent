import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { ErrorState, LoadingState } from '../components/State';

export function TicketsPage() {
  const tickets = useQuery({ queryKey: ['tickets'], queryFn: api.tickets });
  return (
    <section>
      <h1>Tickets</h1>
      {tickets.isLoading && <LoadingState />}
      {tickets.isError && <ErrorState message={tickets.error.message} />}
      <table>
        <thead><tr><th>Ticket ID</th><th>Category</th><th>Priority</th><th>Status</th><th>Created</th></tr></thead>
        <tbody>
          {tickets.data?.map((ticket) => (
            <tr key={ticket.id}><td>{ticket.id}</td><td>{ticket.category}</td><td>{ticket.priority}</td><td>{ticket.status}</td><td>{new Date(ticket.created_at).toLocaleString()}</td></tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

