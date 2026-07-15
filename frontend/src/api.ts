import type { HealthStatus, Shortlink, ShortlinkCreate, ShortlinkUpdate } from "./types";

/** Hosted Shortink API - loaded from env var VITE_HOSTED_API_URL. */
export const HOSTED_API_BASE = import.meta.env.VITE_HOSTED_API_URL as string;

/**
 * - Unset → hosted API (direct).
 * - Empty string (root `.env`) → same-origin paths; Vite proxies to hosted API.
 * - Explicit URL → that origin.
 */
const rawBase = import.meta.env.VITE_API_BASE_URL;
export const API_BASE = (
  rawBase === undefined ? HOSTED_API_BASE : rawBase
).replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: string | { msg?: string }[] };
      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body.detail) && body.detail[0]?.msg) {
        detail = body.detail[0].msg;
      }
    } catch {
      // keep default detail
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  listShortlinks: () => request<Shortlink[]>("/shortlinks"),

  createShortlink: (payload: ShortlinkCreate) =>
    request<Shortlink>("/shortlinks", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  updateShortlink: (id: number, payload: ShortlinkUpdate) =>
    request<Shortlink>(`/shortlinks/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  deleteShortlink: (id: number) =>
    request<void>(`/shortlinks/${id}`, {
      method: "DELETE",
    }),

  health: () => request<HealthStatus>("/health/redis"),
};
