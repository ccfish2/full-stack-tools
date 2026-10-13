// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Navbar } from "./components/navabar.tsx";
import { FeatureFlagPage } from "./pages/core/FeatureFlag.tsx";
import { ReportsPage } from "./pages/reports/ReportsList.tsx";
import "./css/styles.css";
import { AuthProvider } from "./auth/AuthContext.tsx";

export default function App() {
  return (
    <BrowserRouter>
    <AuthProvider>
      <Navbar />
      <Routes>
        {/* Core app routes */}
        <Route path="/core/feature-flag" element={<FeatureFlagPage />} />
        
        {/* Reports app routes */}
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/core/Reports" element={<ReportsPage />} />
        <Route path="/reports/:id" element={<div>Report Detail Page</div>} />
        
        {/* Catch-all redirect */}
        <Route path="/" element={<Navigate to="/core/feature-flag" replace />} />
      </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}