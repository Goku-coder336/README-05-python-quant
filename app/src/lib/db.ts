import pg from "pg";

// One pool per server process. DATABASE_URL comes from .env.local (never committed).
const g = globalThis as unknown as { __pool?: pg.Pool };
export const pool = g.__pool ?? new pg.Pool({ connectionString: process.env.DATABASE_URL, max: 5, ssl: process.env.DATABASE_SSL === "true" ? { rejectUnauthorized: false } : undefined });
if (process.env.NODE_ENV !== "production") g.__pool = pool;

// Postgres returns bigint as string; our money values fit safely in a JS number.
pg.types.setTypeParser(20, v => Number(v));
pg.types.setTypeParser(1700, v => Number(v)); // numeric (ratings)
pg.types.setTypeParser(1082, v => v);          // date stays "YYYY-MM-DD"

export async function q<T = Record<string, unknown>>(sql: string, values: unknown[] = []) {
  return (await pool.query(sql, values)).rows as T[];
}
export async function one<T = Record<string, unknown>>(sql: string, values: unknown[] = []) {
  return (await q<T>(sql, values))[0] ?? null;
}
