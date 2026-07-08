import { Bot, BarChart3, Database, MessagesSquare, Ticket } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';

const nav = [
  { to: '/', label: 'Overview', icon: Bot },
  { to: '/chat', label: 'Chat', icon: MessagesSquare },
  { to: '/knowledge', label: 'Knowledge', icon: Database },
  { to: '/conversations', label: 'Conversations', icon: MessagesSquare },
  { to: '/tickets', label: 'Tickets', icon: Ticket },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 }
];

export default function App() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">NexusAgent</div>
        <nav>
          {nav.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? 'nav active' : 'nav')}>
                <Icon size={18} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}

