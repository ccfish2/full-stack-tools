// src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { FeatureFlagPage } from "./pages/core/FeatureFlag.tsx";
import { ReportsPage } from "./pages/reports/ReportsList.tsx";
import "./css/styles.css";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        {/* Core app routes */}
        <Route path="/core/feature-flag" element={<FeatureFlagPage />} />
        
        {/* Reports app routes */}
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/reports/:id" element={<div>Report Detail Page</div>} />
        
        {/* Catch-all redirect */}
        <Route path="/" element={<Navigate to="/core/feature-flag" replace />} />
      </Routes>
    </BrowserRouter>
  );
}