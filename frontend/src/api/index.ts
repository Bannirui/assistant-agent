import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 60000,
});

export interface AnalyzeResponse {
  ticket_id: string;
  analysis: {
    intent: string;
    emotion: string;
    risk: string;
  };
  reply_template: string;
  suggested_actions: Array<{
    type: string;
    label: string;
    params?: Record<string, any>;
  }>;
  references: Record<string, any>;
  warnings: string[];
}

export async function analyzeTicket(ticketId: string): Promise<AnalyzeResponse> {
  const { data } = await api.post<AnalyzeResponse>("/copilot/analyze", {
    ticket_id: ticketId,
  });
  return data;
}

export async function getStatus() {
  const { data } = await api.get("/copilot/status");
  return data;
}
