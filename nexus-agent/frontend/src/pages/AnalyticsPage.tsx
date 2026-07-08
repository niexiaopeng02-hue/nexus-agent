import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { ErrorState, LoadingState } from '../components/State';

export function AnalyticsPage() {
  const analytics = useQuery({ queryKey: ['analytics'], queryFn: api.analytics });
  if (analytics.isLoading) return <LoadingState />;
  if (analytics.isError) return <ErrorState message={analytics.error.message} />;
  const data = analytics.data;
  return (
    <section>
      <h1>Analytics</h1>
      <div className="grid three">
        <Metric label="Total Conversations" value={data?.total_conversations ?? 0} />
        <Metric label="Knowledge Queries" value={data?.knowledge_queries ?? 0} />
        <Metric label="Tool Calls" value={data?.tool_calls ?? 0} />
        <Metric label="Tickets Created" value={data?.tickets_created ?? 0} />
        <Metric label="Unresolved Questions" value={data?.unresolved_questions ?? 0} />
        <Metric label="Average Response Time" value={`${data?.average_response_time_ms ?? 0} ms`} />
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}

