import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function login(email: string, password: string) {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  const { data } = await api.post("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  localStorage.setItem("access_token", data.access_token);
  return data;
}

export async function register(email: string, password: string, full_name?: string) {
  const { data } = await api.post("/auth/register", { email, password, full_name });
  return data;
}

export async function me() {
  const { data } = await api.get("/auth/me");
  return data;
}

export async function listAnalyses() {
  const { data } = await api.get("/analyses");
  return data;
}

export async function uploadAnalysis(file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/analyses", form);
  return data;
}

export async function getAnalysis(id: string) {
  const { data } = await api.get(`/analyses/${id}`);
  return data;
}

export async function runStep(id: string, step: string) {
  const { data } = await api.post(`/analyses/${id}/${step}`);
  return data;
}

export async function runPipeline(id: string) {
  const { data } = await api.post(`/analyses/${id}/pipeline`);
  return data;
}

export async function getSettings() {
  const { data } = await api.get("/settings");
  return data;
}

export async function updateSettings(settingsData: { api_key?: string; llm_provider?: string; model?: string }) {
  const { data } = await api.post("/settings", settingsData);
  return data;
}

export async function testSettings(settingsData: { api_key?: string; llm_provider?: string }) {
  const { data } = await api.post("/settings/test", settingsData);
  return data;
}
