import axios from "axios";

const api = axios.create({ baseURL: "/admin" });

export interface SopItem {
  id: string;
  category: string;
  issue_types: string[];
  steps: string[];
  compensation_rules: Record<string, any>[];
  templates: Record<string, string>;
  suggested_actions: Record<string, any>[];
}

export async function listSops(): Promise<SopItem[]> {
  const { data } = await api.get("/sop");
  return Array.isArray(data) ? data : [];
}

export async function getSop(id: string): Promise<SopItem> {
  const { data } = await api.get(`/sop/${id}`);
  return data;
}

export async function createSop(sop: SopItem): Promise<any> {
  const { data } = await api.post("/sop", sop);
  return data;
}

export async function updateSop(id: string, sop: SopItem): Promise<any> {
  const { data } = await api.put(`/sop/${id}`, sop);
  return data;
}

export async function deleteSop(id: string): Promise<any> {
  const { data } = await api.delete(`/sop/${id}`);
  return data;
}

export async function reloadSops(): Promise<any> {
  const { data } = await api.post("/sop/reload");
  return data;
}
