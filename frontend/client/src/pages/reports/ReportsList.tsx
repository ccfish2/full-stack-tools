// src/pages/reports/ReportsList.tsx
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getReports, type Report } from "../../api/reports/reports";

export function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getReports()
      .then(setReports)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="app-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">Operations console</p>
          <h1>Reports</h1>
          <p className="page-intro">Analytics and insights for your operations.</p>
        </div>
      </header>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-heading">
            <span className="panel-number">01</span>
            <div><p className="panel-kicker">Analytics</p><h2>Reports</h2></div>
          </div>

          {loading && <p className="empty-state">Loading reports...</p>}
          {error && <p className="error-text">Error: {error}</p>}
          
          {reports.length > 0 ? (
            <div className="reports-list">
              {reports.map((report) => (
                <div key={report.id} className="report-item">
                  <h3>{report.name}</h3>
                  <p>{report.description}</p>
                  <Link to={`/reports/${report.id}`} className="button button-outline">
                    View Details →
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-state">No reports yet.</p>
          )}
        </section>
      </div>
    </main>
  );
}