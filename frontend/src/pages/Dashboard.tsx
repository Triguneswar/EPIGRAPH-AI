import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listAnalyses } from "../services/api";
import { BarChart3, Plus, CheckCircle2, Clock, AlertTriangle, FileText } from "lucide-react";

interface Analysis {
  id: string;
  status: string;
  created_at: string;
  image?: { filename: string } | null;
  translation?: { english: string } | null;
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    COMPLETED: "bg-emerald-50 text-emerald-700 border-emerald-200",
    FAILED: "bg-red-50 text-red-700 border-red-200",
    UPLOADED: "bg-blue-50 text-blue-700 border-blue-200",
  };
  const fallback = "bg-amber-50 text-amber-700 border-amber-200";
  const icons: Record<string, React.ReactNode> = {
    COMPLETED: <CheckCircle2 size={12} />,
    FAILED: <AlertTriangle size={12} />,
    UPLOADED: <Clock size={12} />,
  };

  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full border ${styles[status] || fallback}`}>
      {icons[status] || <Clock size={12} />}
      {status.replace(/_/g, " ")}
    </span>
  );
}

export default function Dashboard() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    listAnalyses()
      .then(setAnalyses)
      .finally(() => setLoading(false));
  }, []);

  const total = analyses.length;
  const completed = analyses.filter((a) => a.status === "COMPLETED").length;
  const failed = analyses.filter((a) => a.status === "FAILED").length;
  const inProgress = total - completed - failed;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-serif font-bold text-ink">Research Dashboard</h1>
          <p className="text-sm text-ink/50 mt-0.5">Your EPIGRAPH-AI inscription analyses</p>
        </div>
        <Link
          to="/analysis/new"
          className="bg-clay text-parchment px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-bronze transition shadow-sm flex items-center gap-2"
        >
          <Plus size={16} />
          New Analysis
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Analyses", value: total, icon: FileText, color: "text-ink" },
          { label: "Completed", value: completed, icon: CheckCircle2, color: "text-emerald-600" },
          { label: "In Progress", value: inProgress, icon: Clock, color: "text-amber-600" },
          { label: "Success Rate", value: total ? `${Math.round((completed / total) * 100)}%` : "—", icon: BarChart3, color: "text-clay" },
        ].map((stat) => (
          <div key={stat.label} className="bg-white/60 border border-ink/10 rounded-xl p-5 hover:shadow-sm transition">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs text-ink/50 font-medium uppercase tracking-wider">{stat.label}</p>
              <stat.icon size={16} className={`${stat.color} opacity-60`} />
            </div>
            <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      {/* Recent Analyses */}
      <div className="bg-white/60 border border-ink/10 rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-ink/5">
          <h2 className="font-semibold text-ink text-sm">Recent Analyses</h2>
        </div>

        {loading ? (
          <div className="p-8 text-center text-ink/50 text-sm">Loading analyses...</div>
        ) : analyses.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <FileText className="mx-auto text-ink/20" size={40} />
            <p className="text-sm text-ink/50">
              No analyses yet —{" "}
              <Link to="/analysis/new" className="text-clay font-medium hover:underline">
                upload your first inscription
              </Link>
            </p>
          </div>
        ) : (
          <div className="divide-y divide-ink/5">
            {analyses.slice(0, 10).map((a) => (
              <Link
                key={a.id}
                to={`/analysis/${a.id}`}
                className="flex items-center justify-between px-5 py-3.5 hover:bg-ink/[0.02] transition group"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-clay/10 flex items-center justify-center flex-shrink-0">
                    <FileText size={14} className="text-clay" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-ink group-hover:text-clay transition truncate">
                      {a.image?.filename || `Analysis ${a.id.slice(0, 8)}`}
                    </p>
                    <p className="text-xs text-ink/40">
                      {new Date(a.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" })}
                    </p>
                  </div>
                </div>
                <StatusBadge status={a.status} />
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
