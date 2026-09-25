// src/api/reports/reports.ts
import { fetcher, post } from "../client";

export interface Report {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

export async function getReports(): Promise<Report[]> {
  const response = await fetcher("/reports/");
  if (response.status >= 400) throw new Error("Failed to fetch reports");
  return await response;  
}

export async function getReportDetail(id: number): Promise<Report> {
  const response = await fetcher(`/reports/${id}/`);
  if (!response.ok) throw new Error("Failed to fetch report");
  return await response;  
}