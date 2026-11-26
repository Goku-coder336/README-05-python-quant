import { headers } from "next/headers";
// Simple per-IP limiter (per server instance). Replace with a shared store (Upstash, Postgres) when running several instances.
const hits = new Map<string, number[]>();
export async function limited(bucket: string, max: number, windowMs: number) {
  const h = await headers();
  const ip = (h.get("x-forwarded-for") ?? "").split(",")[0].trim() || h.get("x-real-ip") || "local";
  const key = `${bucket}:${ip}`; const now = Date.now();
  const list = (hits.get(key) ?? []).filter(t => now - t < windowMs);
  list.push(now); hits.set(key, list);
  return list.length > max;
}
