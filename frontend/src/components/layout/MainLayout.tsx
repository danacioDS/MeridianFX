import { Outlet } from 'react-router-dom';
import { Header } from './Header';

export function MainLayout(): JSX.Element {
  return (
    <div className="max-w-7xl mx-auto px-4 py-4">
      <Header />
      <main className="w-full">
        <Outlet />
      </main>
    </div>
  );
}
