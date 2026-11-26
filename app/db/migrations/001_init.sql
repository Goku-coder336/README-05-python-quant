-- Festora: first migration. Postgres 15+ (Supabase, Neon or local).
-- Authorisation is enforced in src/lib/data.ts on every query (see replica/backend.md).
create extension if not exists btree_gist;
create extension if not exists pgcrypto;

create table countries (
  code char(2) primary key, name text not null, currency char(3) not null, locale text not null,
  tax_name text not null, tax_rate_bp int not null check (tax_rate_bp between 0 and 5000), active boolean not null default false
);
create table regions (
  id text primary key, country_code char(2) not null references countries(code) on delete restrict,
  parent_id text references regions(id) on delete restrict, kind text not null check (kind in ('state','city')),
  name text not null, slug text not null, timezone text not null, active boolean not null default false,
  unique (country_code, kind, slug)
);
create index on regions (parent_id);
create table traditions (id text primary key, slug text unique not null, name text not null);
create table categories (id text primary key, slug text unique not null, name text not null, kind text not null check (kind in ('service','equipment')), icon text not null);

create table users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null check (email = lower(email)),
  name text, role text not null default 'member' check (role in ('member','admin')),
  created_at timestamptz not null default now()
);
create table sessions (
  token_hash text primary key, user_id uuid not null references users(id) on delete cascade,
  expires_at timestamptz not null, created_at timestamptz not null default now()
);
create index on sessions (user_id);
create table login_codes (
  id uuid primary key default gen_random_uuid(), email text not null, code_hash text not null,
  attempts int not null default 0, expires_at timestamptz not null, used_at timestamptz, created_at timestamptz not null default now()
);
create index on login_codes (email, created_at desc);

create table vendors (
  id text primary key default ('v-' || substr(gen_random_uuid()::text,1,12)),
  owner_id uuid references users(id) on delete set null,
  handle text unique not null, business_name text not null, bio text not null default '',
  base_region_id text not null references regions(id) on delete restrict,
  serves_region_ids text[] not null default '{}', phone text not null,
  verification text not null default 'pending' check (verification in ('pending','verified')),
  rating_avg numeric(3,2) not null default 0, rating_count int not null default 0,
  tradition_ids text[] not null default '{}', created_at timestamptz not null default now()
);
create index on vendors (owner_id);
create index on vendors using gin (serves_region_ids);

create table services (
  id text primary key default ('s-' || substr(gen_random_uuid()::text,1,12)),
  vendor_id text not null references vendors(id) on delete cascade,
  category_id text not null references categories(id) on delete restrict,
  title text not null, description text not null default '', included text[] not null default '{}',
  price_minor bigint not null check (price_minor > 0), currency char(3) not null,
  price_unit text not null default 'event' check (price_unit in ('event','day','hour','person')),
  min_guests int, max_guests int, advance_pct int not null default 30 check (advance_pct between 0 and 100),
  styles text[] not null default '{}', tradition_ids text[] not null default '{}',
  status text not null default 'live' check (status in ('draft','live')), created_at timestamptz not null default now()
);
create index on services (vendor_id);
create index on services (category_id, status);

create table equipment (
  id text primary key default ('e-' || substr(gen_random_uuid()::text,1,12)),
  vendor_id text not null references vendors(id) on delete cascade,
  category_id text not null references categories(id) on delete restrict,
  title text not null, description text not null default '', specs jsonb not null default '{}',
  day_rate_minor bigint not null check (day_rate_minor > 0), deposit_minor bigint not null default 0 check (deposit_minor >= 0),
  currency char(3) not null, needs_operator boolean not null default false,
  units int not null default 1 check (units between 1 and 50),
  status text not null default 'live' check (status in ('draft','live')), created_at timestamptz not null default now()
);
create index on equipment (vendor_id);
create index on equipment (category_id, status);

create table bookings (
  id text primary key default ('b-' || substr(gen_random_uuid()::text,1,12)),
  vendor_id text not null references vendors(id) on delete restrict,
  customer_id uuid references users(id) on delete set null,
  item_kind text not null check (item_kind in ('service','equipment')), item_id text not null, item_title text not null,
  customer_name text not null, customer_phone text not null, note text not null default '',
  starts_on date not null, ends_on date not null, unit_index int,
  subtotal_minor bigint not null, tax_minor bigint not null default 0, deposit_minor bigint not null default 0, currency char(3) not null,
  status text not null default 'requested' check (status in ('requested','accepted','declined','cancelled','completed')),
  created_at timestamptz not null default now(),
  constraint booking_window check (ends_on >= starts_on)
);
create index on bookings (vendor_id, created_at desc);
create index on bookings (customer_id);

-- The database itself refuses double bookings:
-- one physical gear unit cannot be held twice for overlapping days,
-- and one vendor cannot hold two service bookings on the same day.
create table unit_holds (
  booking_id text primary key references bookings(id) on delete cascade,
  equipment_id text not null references equipment(id) on delete cascade,
  unit_index int not null, period daterange not null,
  exclude using gist (equipment_id with =, unit_index with =, period with &&)
);
create table vendor_day_holds (
  booking_id text primary key references bookings(id) on delete cascade,
  vendor_id text not null references vendors(id) on delete cascade, period daterange not null,
  exclude using gist (vendor_id with =, period with &&)
);

create table waitlist (
  id uuid primary key default gen_random_uuid(), email text not null check (email = lower(email)),
  role text not null check (role in ('customer','vendor')), city text not null,
  created_at timestamptz not null default now(), unique (email, role)
);

create table schema_migrations (name text primary key, applied_at timestamptz not null default now());
