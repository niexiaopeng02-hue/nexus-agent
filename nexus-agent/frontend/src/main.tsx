import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ChatPage } from './pages/ChatPage';
import { ConversationsPage } from './pages/ConversationsPage';
import { KnowledgeBasePage } from './pages/KnowledgeBasePage';
import { LandingPage } from './pages/LandingPage';
import { TicketsPage } from './pages/TicketsPage';
import './styles.css';

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <LandingPage /> },
      { path: 'chat', element: <ChatPage /> },
      { path: 'knowledge', element: <KnowledgeBasePage /> },
      { path: 'conversations', element: <ConversationsPage /> },
      { path: 'tickets', element: <TicketsPage /> },
      { path: 'analytics', element: <AnalyticsPage /> }
    ]
  }
]);

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>
);

