import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';
import { EmptyState, ErrorState, LoadingState } from '../components/State';

export function KnowledgeBasePage() {
  const queryClient = useQueryClient();
  const documents = useQuery({ queryKey: ['documents'], queryFn: api.documents });
  const upload = useMutation({ mutationFn: api.uploadDocument, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] }) });
  const remove = useMutation({ mutationFn: api.deleteDocument, onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] }) });

  return (
    <section>
      <h1>Knowledge Base</h1>
      <input type="file" accept=".pdf,.docx,.txt,.md,.markdown" onChange={(event) => event.target.files?.[0] && upload.mutate(event.target.files[0])} />
      {upload.isError && <ErrorState message={upload.error.message} />}
      {documents.isLoading && <LoadingState />}
      {documents.isError && <ErrorState message={documents.error.message} />}
      {documents.data?.length === 0 && <EmptyState message="No documents have been ingested yet." />}
      <table>
        <thead><tr><th>Name</th><th>Status</th><th>Chunks</th><th>Uploaded</th><th></th></tr></thead>
        <tbody>
          {documents.data?.map((doc) => (
            <tr key={doc.id}>
              <td>{doc.name}</td><td>{doc.status}</td><td>{doc.chunk_count}</td><td>{new Date(doc.uploaded_at).toLocaleString()}</td>
              <td><button onClick={() => remove.mutate(doc.id)}>Delete</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

