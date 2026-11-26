// Applies db/migrations/*.sql in order, once each. Usage: npm run db:migrate
import fs from "node:fs"; import path from "node:path"; import pg from "pg";
const url = process.env.DATABASE_URL; if (!url) { console.error("DATABASE_URL is not set"); process.exit(1); }
const c = new pg.Client({ connectionString: url }); await c.connect();
await c.query("create table if not exists schema_migrations (name text primary key, applied_at timestamptz not null default now())");
const done = new Set((await c.query("select name from schema_migrations")).rows.map(r => r.name));
const dir = path.resolve("db/migrations");
for (const f of fs.readdirSync(dir).filter(f => f.endsWith(".sql")).sort()) {
  if (done.has(f)) continue;
  const sql = fs.readFileSync(path.join(dir, f), "utf8").replace(/create table schema_migrations[^;]*;/i, "");
  await c.query("begin"); try { await c.query(sql); await c.query("insert into schema_migrations(name) values($1)", [f]); await c.query("commit"); console.log("applied", f); }
  catch (e) { await c.query("rollback"); console.error("failed", f, e.message); process.exit(1); }
}
await c.end();
