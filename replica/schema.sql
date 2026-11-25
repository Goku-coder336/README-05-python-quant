-- Event services + equipment rental marketplace. First migration.
-- Postgres (Supabase). All times timestamptz in UTC. Money = integer minor units + currency.
-- Access: Supabase row level security (policies at the bottom).

create extension if not exists btree_gist;
create extension if not exists pg_trgm;

-- ---------- places and culture ----------

create table countries (
  code char(2) primary key,                 -- IN, AE, GB, US, CA, AU
  name text not null,
  currency char(3) not null,                -- INR, AED, GBP, USD, CAD, AUD
  default_locale text not null,             -- en-IN, ar-AE, en-GB
  tax_name text not null,                   -- GST, VAT, Sales tax
  tax_rate_bp int not null default 0,       -- basis points, 1800 = 18%
  payment_provider text not null check (payment_provider in ('razorpay','stripe')),
  active boolean not null default false
);

create table regions (                        -- state, emirate, nation; then city; then area
  id uuid primary key default gen_random_uuid(),
  country_code char(2) not null references countries(code) on delete restrict,
  parent_id uuid references regions(id) on delete restrict,
  kind text not null check (kind in ('state','city','area')),
  name text not null,
  slug text not null,
  timezone text not null,                   -- Asia/Kolkata, Asia/Dubai, Europe/London
  languages text[] not null default '{}',   -- {ml,en}, {ta,en}, {ar,en}
  active boolean not null default false,    -- a city opens only when it has supply
  created_at timestamptz not null default now(),
  unique (country_code, slug)
);
create index on regions (parent_id);

create table traditions (                     -- culture/community styles, e.g. kerala-hindu, kerala-christian, kerala-muslim, tamil-brahmin, punjabi-sikh, western
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  description text,
  region_hints uuid[] not null default '{}' -- where it is common; used for defaults, never to restrict
);

create table event_types (                    -- wedding, engagement, mehndi/haldi, baptism, nikah, birthday, corporate, intimate-dinner, proposal...
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  parent_id uuid references event_types(id) on delete restrict -- e.g. haldi under wedding
);

create table categories (                     -- what can be booked or rented
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  kind text not null check (kind in ('service','equipment')),
  parent_id uuid references categories(id) on delete restrict
);
-- service examples: event-management, makeup, mehendi, photography, videography, catering, decor, dj, anchor, priest/officiant
-- equipment examples: sound, lighting, led-wall, generator, stage-truss, tents, furniture, camera-gear

create table style_tags (                     -- candid, cinematic, traditional, drone, minimal, luxury, eco, intimate
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null
);

-- Planner template: for a tradition + event type + size, what does the customer need?
create table event_templates (
  id uuid primary key default gen_random_uuid(),
  event_type_id uuid not null references event_types(id) on delete cascade,
  tradition_id uuid references traditions(id) on delete cascade,   -- null = any
  country_code char(2) references countries(code) on delete cascade,
  size_tier text not null check (size_tier in ('intimate','medium','large')), -- intimate <= 50 guests
  title text not null,
  unique nulls not distinct (event_type_id, tradition_id, country_code, size_tier)
);
create table event_template_items (
  id uuid primary key default gen_random_uuid(),
  template_id uuid not null references event_templates(id) on delete cascade,
  category_id uuid not null references categories(id) on delete restrict,
  sub_event text,                           -- e.g. 'haldi', 'reception'
  required boolean not null default true,
  note text,                                -- e.g. 'Kasavu saree draping', 'nilavilakku lamp'
  sort int not null default 0
);
create index on event_template_items (template_id);

-- ---------- people ----------

create table profiles (                       -- 1:1 with auth.users
  id uuid primary key references auth.users(id) on delete cascade,
  full_name text,
  phone text,
  role text not null default 'customer' check (role in ('customer','vendor','admin')),
  locale text not null default 'en-IN',
  home_region_id uuid references regions(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table vendors (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references profiles(id) on delete cascade,
  handle text unique not null,
  business_name text not null,
  bio text,
  base_region_id uuid not null references regions(id) on delete restrict,
  serves_region_ids uuid[] not null default '{}',
  travel_note text,
  languages text[] not null default '{}',
  verification text not null default 'pending' check (verification in ('pending','verified','rejected','suspended')),
  rating_avg numeric(3,2) not null default 0,
  rating_count int not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index on vendors (owner_id);
create index on vendors (base_region_id);
create index on vendors using gin (serves_region_ids);

create table vendor_traditions (               -- "experienced in Kerala Christian weddings"
  vendor_id uuid references vendors(id) on delete cascade,
  tradition_id uuid references traditions(id) on delete cascade,
  primary key (vendor_id, tradition_id)
);

-- ---------- what is sold ----------

create table services (                        -- a package: "Candid wedding photography, 2 days"
  id uuid primary key default gen_random_uuid(),
  vendor_id uuid not null references vendors(id) on delete cascade,
  category_id uuid not null references categories(id) on delete restrict,
  title text not null,
  description text,
  included text[] not null default '{}',
  price_minor bigint not null check (price_minor >= 0),
  currency char(3) not null,
  price_unit text not null default 'event' check (price_unit in ('event','day','hour','person')),
  min_guests int, max_guests int,           -- lets intimate events filter cleanly
  advance_pct int not null default 30 check (advance_pct between 0 and 100),
  cancellation_policy text,
  style_tag_ids uuid[] not null default '{}',
  tradition_ids uuid[] not null default '{}',
  bundled_equipment_id uuid,                -- set below: "PA system + engineer"
  status text not null default 'draft' check (status in ('draft','live','paused')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index on services (vendor_id);
create index on services (category_id, status);
create index on services using gin (style_tag_ids);
create index on services using gin (tradition_ids);
create index on services using gin (title gin_trgm_ops);

create table equipment (                       -- a rentable product line: "JBL VRX932 line array"
  id uuid primary key default gen_random_uuid(),
  vendor_id uuid not null references vendors(id) on delete cascade,
  category_id uuid not null references categories(id) on delete restrict,
  title text not null,
  description text,
  specs jsonb not null default '{}',        -- watts, kVA, size
  day_rate_minor bigint not null check (day_rate_minor >= 0),
  deposit_minor bigint not null default 0 check (deposit_minor >= 0),
  currency char(3) not null,
  delivery text not null default 'pickup' check (delivery in ('pickup','delivery','both')),
  needs_operator boolean not null default false,
  status text not null default 'draft' check (status in ('draft','live','paused')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index on equipment (vendor_id);
create index on equipment (category_id, status);
alter table services add constraint services_bundle_fk
  foreign key (bundled_equipment_id) references equipment(id) on delete set null;

create table equipment_units (                  -- each physical item; availability is per unit
  id uuid primary key default gen_random_uuid(),
  equipment_id uuid not null references equipment(id) on delete cascade,
  label text not null,                      -- "Unit 1"
  condition text not null default 'good' check (condition in ('good','repair','retired'))
);
create index on equipment_units (equipment_id);

create table media (
  id uuid primary key default gen_random_uuid(),
  owner_kind text not null check (owner_kind in ('vendor','service','equipment','booking_handover')),
  owner_id uuid not null,
  path text not null,                       -- storage key
  kind text not null check (kind in ('image','video')),
  sort int not null default 0
);
create index on media (owner_kind, owner_id);

-- ---------- the customer's event (everything in one place) ----------

create table events (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references profiles(id) on delete cascade,
  event_type_id uuid not null references event_types(id) on delete restrict,
  tradition_id uuid references traditions(id) on delete set null,
  region_id uuid not null references regions(id) on delete restrict,
  title text not null,                      -- "Anu & Joel's wedding"
  guest_count int,
  size_tier text not null check (size_tier in ('intimate','medium','large')),
  budget_minor bigint, currency char(3) not null,
  starts_on date, ends_on date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index on events (customer_id);

create table event_checklist (                 -- copied from the template, then the customer edits it
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references events(id) on delete cascade,
  category_id uuid not null references categories(id) on delete restrict,
  sub_event text,
  status text not null default 'todo' check (status in ('todo','shortlisted','booked','skipped')),
  note text
);
create index on event_checklist (event_id);

create table shortlist (
  event_id uuid references events(id) on delete cascade,
  item_kind text not null check (item_kind in ('service','equipment')),
  item_id uuid not null,
  primary key (event_id, item_kind, item_id)
);

-- ---------- enquiries, bookings, money ----------

create table enquiries (
  id uuid primary key default gen_random_uuid(),
  event_id uuid references events(id) on delete set null,
  customer_id uuid not null references profiles(id) on delete cascade,
  vendor_id uuid not null references vendors(id) on delete cascade,
  item_kind text check (item_kind in ('service','equipment')),
  item_id uuid,
  message text not null,
  status text not null default 'open' check (status in ('open','quoted','won','lost','closed')),
  quote_minor bigint, currency char(3),
  created_at timestamptz not null default now()
);
create index on enquiries (vendor_id, status);
create index on enquiries (customer_id);

create table bookings (
  id uuid primary key default gen_random_uuid(),
  event_id uuid references events(id) on delete set null,
  customer_id uuid not null references profiles(id) on delete restrict,
  vendor_id uuid not null references vendors(id) on delete restrict,
  status text not null default 'requested'
    check (status in ('requested','accepted','paid_advance','in_progress','completed','cancelled','disputed')),
  starts_at timestamptz not null,
  ends_at timestamptz not null,
  subtotal_minor bigint not null,
  tax_minor bigint not null default 0,
  fee_minor bigint not null default 0,       -- platform commission
  deposit_minor bigint not null default 0,   -- held, not charged
  currency char(3) not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint booking_window check (ends_at > starts_at)
);
create index on bookings (vendor_id, starts_at);
create index on bookings (customer_id);

create table booking_lines (
  id uuid primary key default gen_random_uuid(),
  booking_id uuid not null references bookings(id) on delete cascade,
  item_kind text not null check (item_kind in ('service','equipment')),
  service_id uuid references services(id) on delete restrict,
  equipment_unit_id uuid references equipment_units(id) on delete restrict,
  qty int not null default 1,
  price_minor bigint not null,
  check ((item_kind = 'service' and service_id is not null) or (item_kind = 'equipment' and equipment_unit_id is not null))
);
create index on booking_lines (booking_id);

-- No double booking of a physical unit: one row per unit per active booking window.
create table unit_holds (
  id uuid primary key default gen_random_uuid(),
  equipment_unit_id uuid not null references equipment_units(id) on delete cascade,
  booking_id uuid references bookings(id) on delete cascade,
  period tstzrange not null,                -- includes setup and return buffer
  reason text not null default 'booking' check (reason in ('booking','blocked','maintenance')),
  exclude using gist (equipment_unit_id with =, period with &&)
);

create table vendor_blackouts (                -- a photographer's busy dates
  id uuid primary key default gen_random_uuid(),
  vendor_id uuid not null references vendors(id) on delete cascade,
  period tstzrange not null
);
create index on vendor_blackouts using gist (vendor_id, period);

create table payments (
  id uuid primary key default gen_random_uuid(),
  booking_id uuid not null references bookings(id) on delete restrict,
  provider text not null check (provider in ('razorpay','stripe')),
  provider_ref text not null,
  kind text not null check (kind in ('advance','balance','deposit_hold','deposit_release','deposit_capture','refund','payout')),
  amount_minor bigint not null,
  currency char(3) not null,
  status text not null check (status in ('pending','succeeded','failed')),
  created_at timestamptz not null default now(),
  unique (provider, provider_ref, kind)     -- webhook idempotency
);
create index on payments (booking_id);

create table handovers (                       -- equipment out/in checklist with photos
  id uuid primary key default gen_random_uuid(),
  booking_id uuid not null references bookings(id) on delete cascade,
  direction text not null check (direction in ('out','in')),
  checked_by uuid not null references profiles(id) on delete restrict,
  notes text,
  damage boolean not null default false,
  created_at timestamptz not null default now()
);

create table reviews (
  id uuid primary key default gen_random_uuid(),
  booking_id uuid unique not null references bookings(id) on delete cascade,
  vendor_id uuid not null references vendors(id) on delete cascade,
  customer_id uuid not null references profiles(id) on delete cascade,
  rating int not null check (rating between 1 and 5),
  body text,
  created_at timestamptz not null default now()
);
create index on reviews (vendor_id);

create table webhook_events (
  id text primary key,                      -- provider event id
  provider text not null,
  received_at timestamptz not null default now()
);

-- ---------- row level security (summary; full policies in the migration) ----------
alter table profiles enable row level security;
alter table vendors enable row level security;
alter table services enable row level security;
alter table equipment enable row level security;
alter table events enable row level security;
alter table event_checklist enable row level security;
alter table enquiries enable row level security;
alter table bookings enable row level security;
alter table payments enable row level security;
-- public: read live services/equipment and verified vendors
-- vendor: full access to rows where vendors.owner_id = auth.uid()
-- customer: own events, checklist, enquiries, bookings
-- payments, handovers, webhook_events: server (service role) writes only
