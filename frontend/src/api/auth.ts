import { apiClient, TOKEN_STORAGE_KEY } from "./client";
import type { LoginRequest, TokenResponse, UserRead } from "../types/auth";

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>("/auth/login", payload);
  localStorage.setItem(TOKEN_STORAGE_KEY, response.data.access_token);
  return response.data;
}

export async function getCurrentUser(): Promise<UserRead> {
  const response = await apiClient.get<UserRead>("/auth/me");
  return response.data;
}

export function logout(): void {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}
