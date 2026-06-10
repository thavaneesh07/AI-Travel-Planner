import apiClient from "./client";
import { User } from "./types";

export async function register(payload: any): Promise<any> {
  const res = await apiClient.post("/auth/register", payload);
  return res.data;
}

export async function login(payload: any): Promise<any> {
  const res = await apiClient.post("/auth/login", payload);
  return res.data;
}

export async function getMe(): Promise<User> {
  const res = await apiClient.get("/auth/me");
  return res.data;
}
