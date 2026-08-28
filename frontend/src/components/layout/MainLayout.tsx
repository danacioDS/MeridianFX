/**
 * Main layout.
 *
 * Composes Sidebar + Header + routed content. The sidebar collapses on
 * tablet (768px+) to a compact rail; desktop shows full width.
 */
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export function MainLayout(): JSX.Element {
  return (
    <div className="flex h-full min-h-screen">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}