import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Footer } from './Footer';

export function MainLayout(): JSX.Element {
  return (
    <div className="max-w-7xl mx-auto px-4 py-4 min-h-screen flex flex-col">
      <Header />
      <main className="w-full flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
