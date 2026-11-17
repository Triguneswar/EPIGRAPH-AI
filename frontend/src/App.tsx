import { Route, Routes, Navigate } from "react-router-dom";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import NewAnalysis from "./pages/NewAnalysis";
import AnalysisResult from "./pages/AnalysisResult";
import History from "./pages/History";
import About from "./pages/About";
import AppLayout from "./layouts/AppLayout";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/about" element={<About />} />

      <Route element={<AppLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/new" element={<NewAnalysis />} />
        <Route path="/analysis/new" element={<NewAnalysis />} />
        <Route path="/analysis/:id" element={<AnalysisResult />} />
        <Route path="/history" element={<History />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
