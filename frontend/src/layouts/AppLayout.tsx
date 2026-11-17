import { NavLink, Outlet } from "react-router-dom";
import { LayoutDashboard, ScanSearch, History, Scroll } from "lucide-react";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/analysis/new", label: "New Analysis", icon: ScanSearch },
  { to: "/history", label: "History", icon: History },
];

export default function AppLayout() {
  return (
    <div className="min-h-screen flex bg-parchment">
      <aside className="w-60 bg-ink text-parchment flex flex-col p-4 shadow-xl">
        <div className="flex items-center gap-2.5 mb-8 px-2 pt-2">
          <div className="w-8 h-8 rounded-lg bg-clay/20 flex items-center justify-center text-bronze">
            <Scroll size={20} />
          </div>
          <span className="font-bold tracking-wide text-base">EPIGRAPH-AI</span>
        </div>
        <nav className="flex-1 space-y-1.5">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg text-sm transition font-medium ${
                  isActive ? "bg-clay text-parchment shadow-sm" : "hover:bg-white/10 text-parchment/80"
                }`
              }
            >
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="pt-4 border-t border-white/10 text-xs text-parchment/40 px-2">
          EPIGRAPH-AI · Active Session
        </div>
      </aside>
      <main className="flex-1 p-8 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
