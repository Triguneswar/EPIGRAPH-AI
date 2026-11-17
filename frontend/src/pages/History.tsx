import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listAnalyses } from "../services/api";
import { Search, FileText, CheckCircle2, Clock, AlertTriangle, Trash2, ArrowRight } from "lucide-react";
import { api } from "../services/api";

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

export default function History() {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const [deleting, setDeleting] = useState<string | null>(null);

  useEffect(() => {
    listAnalyses().then(setAnalyses);
  }, []);

  const filtered = analyses.filter(
    (a) => a.id.includes(query) || a.status.includes(query.toUpperCase()) || (a.image?.filename || "").toLowerCase().includes(query.toLowerCase())
  );

  async function handleDelete(id: string) {
    if (!confirm("Delete this analysis? This cannot be undone.")) return;
    setDeleting(id);
    try {
      await api.delete(`/analyses/${id}`);
      setAnalyses((prev) => prev.filter((a) => a.id !== id));
    } catch {
      alert("Failed to delete");
    } finally {
      setDeleting(null);
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-serif font-bold text-ink">Analysis History</h1>
          <p className="text-sm text-ink/50 mt-0.5">{analyses.length} total analyses</p>
        </div>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink/40" />
        <input
          placeholder="Search by filename, ID, or status..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="border border-ink/15 rounded-lg pl-9 pr-3 py-2.5 bg-white w-full text-sm focus:ring-2 focus:ring-clay/30 focus:border-clay outline-none transition"
        />
      </div>

      {/* Table */}
      <div className="bg-white/60 border border-ink/10 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-ink/[0.03] text-left border-b border-ink/10">
            <tr>
              <th className="px-5 py-3 text-xs font-semibold text-ink/50 uppercase tracking-wider">File</th>
              <th className="px-5 py-3 text-xs font-semibold text-ink/50 uppercase tracking-wider">Date</th>
              <th className="px-5 py-3 text-xs font-semibold text-ink/50 uppercase tracking-wider">Status</th>
              <th className="px-5 py-3 text-xs font-semibold text-ink/50 uppercase tracking-wider text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink/5">
            {filtered.map((a) => (
              <tr key={a.id} className="hover:bg-ink/[0.02] transition group">
                <td className="px-5 py-3.5">
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-md bg-clay/10 flex items-center justify-center flex-shrink-0">
                      <FileText size={13} className="text-clay" />
                    </div>
                    <div>
                      <p className="font-medium text-ink">{a.image?.filename || `Analysis ${a.id.slice(0, 8)}`}</p>
                      <p className="text-xs text-ink/40 font-mono">{a.id.slice(0, 12)}…</p>
                    </div>
                  </div>
                </td>
                <td className="px-5 py-3.5 text-ink/60">
                  {new Date(a.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}
                </td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={a.status} />
                </td>
                <td className="px-5 py-3.5 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <Link
                      to={`/analysis/${a.id}`}
                      className="inline-flex items-center gap-1 text-xs text-clay hover:text-bronze font-medium transition"
                    >
                      View <ArrowRight size={12} />
                    </Link>
                    <button
                      onClick={() => handleDelete(a.id)}
                      disabled={deleting === a.id}
                      className="text-ink/30 hover:text-red-500 transition disabled:opacity-30"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr>
                <td colSpan={4} className="px-5 py-12 text-center text-ink/40">
                  <Search className="mx-auto mb-2 opacity-30" size={28} />
                  <p>No analyses found matching "{query}"</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
