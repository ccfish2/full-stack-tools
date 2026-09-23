// src/api/reports/reports.ts
export interface Report {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

export async function getReports(): Promise<Report[]> {
  const response = await fetch("/api/reports/");
  if (!response.ok) throw new Error("Failed to fetch reports");
  return response.json();
}

export async function getReportDetail(id: number): Promise<Report> {
  const response = await fetch(`/api/reports/${id}/`);
  if (!response.ok) throw new Error("Failed to fetch report");
  return response.json();
}