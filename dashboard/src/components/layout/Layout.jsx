import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import useApiHealth from "../../hooks/useApiHealth";

export default function Layout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const connectionOk = useApiHealth();

  return (
    <div className="flex min-h-screen bg-ink-50">
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar onMenuClick={() => setMenuOpen(true)} connectionOk={connectionOk} />
        <main className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
