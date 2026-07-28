import axios from "axios";

const api = axios.create({ baseURL: "/admin/knowledge" });

export interface KnowledgeDoc {
  id: number;
  title: string;
  content: string;
  source: string;
  status?: string;
}

export async function listDocs(): Promise<KnowledgeDoc[]> {
  const { data } = await api.get("/docs");
  return Array.isArray(data) ? data : [];
}

export async function getDoc(id: number): Promise<KnowledgeDoc> {
  const { data } = await api.get(`/docs/${id}`);
  return data;
}

export async function createDoc(doc: { title: string; content: string; source: string }): Promise<any> {
  const { data } = await api.post("/docs", doc);
  return data;
}

export async function updateDoc(id: number, doc: { title: string; content: string; source: string }): Promise<any> {
  const { data } = await api.put(`/docs/${id}`, doc);
  return data;
}

export async function deleteDoc(id: number): Promise<any> {
  const { data } = await api.delete(`/docs/${id}`);
  return data;
}

export async function ingestDocs(): Promise<any> {
  const { data } = await api.post("/ingest");
  return data;
}
