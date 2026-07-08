import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { ErrorState, LoadingState } from '../components/State';

export function ConversationsPage() {
  const [selected, setSelected] = useState<string>();
  const conversations = useQuery({ queryKey: ['conversations'], queryFn: api.conversations });
  const detail = useQuery({ queryKey: ['conversation', selected], queryFn: () => api.conversation(selected!), enabled: Boolean(selected) });

  return (
    <section>
      <h1>Conversations</h1>
      {conversations.isLoading && <LoadingState />}
      {conversations.isError && <ErrorState message={conversations.error.message} />}
      <div className="split">
        <div>
          {conversations.data?.map((item) => (
            <button className="list-button" key={item.id} onClick={() => setSelected(item.id)}>
              {item.title}<span>{item.message_count} messages | {item.last_intent ?? 'none'}</span>
            </button>
          ))}
        </div>
        <div>
          {detail.data?.messages?.map((message) => (
            <article className="message" key={message.id}>
              <strong>{message.role}</strong>
              <p>{message.content}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

