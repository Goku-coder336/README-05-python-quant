// Builds db/setup/supabase-setup.sql from every migration in order, plus reference data
// (countries, cities, traditions, categories) from src/lib/seed.ts. No sample vendors or bookings.
// Usage: npm run db:build-setup   (re-run whenever a migration is added)
import fs from "node:fs";
import path from "node:path";
import { seed } from "../src/lib/seed.ts";

const dir = path.resolve("db/migrations");
const files = fs.readdirSync(dir).filter(f => f.endsWith(".sql")).sort();
const s = (v: unknown) => v === null || v === undefined ? "null" : typeof v === "boolean" ? String(v) : typeof v === "number" ? String(v) : `'${String(v).replace(/'/g, "''")}'`;
const ref = [
  "-- ---------- reference data (countries, cities, traditions, categories) ----------",
  ...seed.countries.map(x => `insert into countries values (${[x.code, x.name, x.currency, x.locale, x.taxName, x.taxRateBp, x.active].map(s).join(", ")}) on conflict do nothing;`),
  ...[...seed.regions].sort((a, b) => Number(!!a.parentId) - Number(!!b.parentId)).map(x => `insert into regions values (${[x.id, x.countryCode, x.parentId, x.kind, x.name, x.slug, x.timezone, x.active].map(s).join(", ")}) on conflict do nothing;`),
  ...seed.traditions.map(x => `insert into traditions (id, slug, name) values (${[x.id, x.slug, x.name].map(s).join(", ")}) on conflict do nothing;`),
  ...seed.categories.map(x => `insert into categories (id, slug, name, kind, icon) values (${[x.id, x.slug, x.name, x.kind, x.icon].map(s).join(", ")}) on conflict do nothing;`),
].join("\n");

const parts: string[] = [`-- =====================================================================
-- Utsella: one-time database setup for Supabase (generated, do not edit by hand)
-- How to use: Supabase dashboard > SQL Editor > New query > paste this
-- whole file > Run. Run it ONCE on an empty project.
-- Creates every table and loads reference data (countries, cities,
-- traditions, vendor categories, event types and their checklists).
-- Does NOT add sample vendors or bookings.
-- Runs in one transaction: if any part fails, nothing is kept.
-- Built from: ${files.join(", ")}
-- =====================================================================
begin;
`];
files.forEach((f, i) => {
  let sql = fs.readFileSync(path.join(dir, f), "utf8");
  if (f === "001_init.sql") sql = sql.replace(/^create table schema_migrations/m, "create table if not exists schema_migrations");
  parts.push(`-- ---------- ${f} ----------\n${sql.trim()}\n`);
  if (i === 0) parts.push(ref + "\n"); // later migrations refer to these rows
});
parts.push(`-- ---------- record applied migrations, so \`npm run db:migrate\` skips them later ----------
insert into schema_migrations (name) values ${files.map(f => `('${f}')`).join(", ")} on conflict do nothing;

-- ---------- security on Supabase ----------
-- Utsella's server talks to the database directly. Supabase's public Data API must not
-- expose these tables, even if it is switched on: row level security with no policies
-- blocks the public roles, and their table permissions are removed.
do $$
declare t record;
begin
  for t in select tablename from pg_tables where schemaname = 'public' loop
    execute format('alter table public.%I enable row level security', t.tablename);
  end loop;
  if exists (select 1 from pg_roles where rolname = 'anon') then
    execute 'revoke all on all tables in schema public from anon, authenticated';
    execute 'revoke all on all sequences in schema public from anon, authenticated';
    execute 'alter default privileges in schema public revoke all on tables from anon, authenticated';
  end if;
end $$;

commit;

-- Check what was created:
select (select count(*) from pg_tables where schemaname = 'public') as tables,
       (select count(*) from event_types) as event_types,
       (select count(*) from event_template_items) as checklist_items,
       (select count(*) from regions where kind = 'city') as cities;
`);
fs.writeFileSync("db/setup/supabase-setup.sql", parts.join("\n"));
console.log(`Wrote db/setup/supabase-setup.sql from ${files.length} migrations.`);
