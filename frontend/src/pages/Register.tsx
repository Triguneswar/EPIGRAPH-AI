import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { register, login } from "../services/api";
import { Scroll, Eye, EyeOff } from "lucide-react";

export default function Register() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(email, password, fullName);
      await login(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-parchment">
      <form
        onSubmit={handleSubmit}
        className="bg-white/60 backdrop-blur-sm border border-ink/10 rounded-2xl p-8 w-full max-w-sm space-y-5 shadow-lg"
      >
        <div className="text-center space-y-1">
          <div className="flex items-center justify-center gap-2 text-clay mb-2">
            <Scroll size={24} />
            <span className="font-bold tracking-wide text-lg">EPIGRAPH-AI</span>
          </div>
          <h1 className="text-xl font-serif font-semibold text-ink">Create an account</h1>
          <p className="text-xs text-ink/50">Join EPIGRAPH-AI to analyze inscriptions</p>
        </div>

        {error && (
          <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg p-2.5 text-center">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm mb-1.5 text-ink/70 font-medium">Full name</label>
          <input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Dr. Indiana Jones"
            className="w-full border border-ink/20 rounded-lg px-3.5 py-2.5 bg-white focus:ring-2 focus:ring-clay/30 focus:border-clay outline-none transition"
          />
        </div>

        <div>
          <label className="block text-sm mb-1.5 text-ink/70 font-medium">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@university.edu"
            className="w-full border border-ink/20 rounded-lg px-3.5 py-2.5 bg-white focus:ring-2 focus:ring-clay/30 focus:border-clay outline-none transition"
          />
        </div>

        <div>
          <label className="block text-sm mb-1.5 text-ink/70 font-medium">Password (min 8 characters)</label>
          <div className="relative">
            <input
              type={showPw ? "text" : "password"}
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full border border-ink/20 rounded-lg px-3.5 py-2.5 bg-white focus:ring-2 focus:ring-clay/30 focus:border-clay outline-none transition pr-10"
            />
            <button
              type="button"
              onClick={() => setShowPw(!showPw)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/40 hover:text-ink/70"
            >
              {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-clay text-parchment py-2.5 rounded-lg font-medium hover:bg-bronze transition disabled:opacity-50 shadow-sm"
        >
          {loading ? "Creating account..." : "Create account"}
        </button>

        <p className="text-sm text-center text-ink/60">
          Already have an account?{" "}
          <Link to="/login" className="text-clay font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </div>
  );
}
