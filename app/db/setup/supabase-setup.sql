-- =====================================================================
-- Utsella: one-time database setup for Supabase (generated, do not edit by hand)
-- How to use: Supabase dashboard > SQL Editor > New query > paste this
-- whole file > Run. Run it ONCE on an empty project.
-- Creates every table and loads reference data (countries, cities,
-- traditions, vendor categories, event types and their checklists).
-- Does NOT add sample vendors or bookings.
-- Runs in one transaction: if any part fails, nothing is kept.
-- Built from: 001_init.sql, 001a_base_data.sql, 002_planner.sql, 003_admin.sql, 004_media.sql, 005_notifications.sql, 006_all_events.sql, 007_reviews.sql, 008_availability.sql
-- =====================================================================
begin;

-- ---------- 001_init.sql ----------
-- Utsella: first migration. Postgres 15+ (Supabase, Neon or local).
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

create table if not exists schema_migrations (name text primary key, applied_at timestamptz not null default now());

-- ---------- reference data (countries, cities, traditions, categories) ----------
insert into countries values ('IN', 'India', 'INR', 'en-IN', 'GST', 1800, true) on conflict do nothing;
insert into countries values ('AE', 'United Arab Emirates', 'AED', 'en-AE', 'VAT', 500, true) on conflict do nothing;
insert into countries values ('GB', 'United Kingdom', 'GBP', 'en-GB', 'VAT', 2000, false) on conflict do nothing;
insert into regions values ('r-kl', 'IN', null, 'state', 'Kerala', 'kerala', 'Asia/Kolkata', true) on conflict do nothing;
insert into regions values ('r-ka', 'IN', null, 'state', 'Karnataka', 'karnataka', 'Asia/Kolkata', true) on conflict do nothing;
insert into regions values ('r-tn', 'IN', null, 'state', 'Tamil Nadu', 'tamil-nadu', 'Asia/Kolkata', true) on conflict do nothing;
insert into regions values ('r-dxb-e', 'AE', null, 'state', 'Dubai', 'dubai-emirate', 'Asia/Dubai', true) on conflict do nothing;
insert into regions values ('c-kochi', 'IN', 'r-kl', 'city', 'Kochi', 'kochi', 'Asia/Kolkata', true) on conflict do nothing;
insert into regions values ('c-tvm', 'IN', 'r-kl', 'city', 'Trivandrum', 'trivandrum', 'Asia/Kolkata', true) on conflict do nothing;
insert into regions values ('c-clt', 'IN', 'r-kl', 'city', 'Calicut', 'calicut', 'Asia/Kolkata', true) on conflict do nothing;
insert into regions values ('c-tcr', 'IN', 'r-kl', 'city', 'Thrissur', 'thrissur', 'Asia/Kolkata', true) on conflict do nothing;
insert into regions values ('c-blr', 'IN', 'r-ka', 'city', 'Bengaluru', 'bengaluru', 'Asia/Kolkata', true) on conflict do nothing;
insert into regions values ('c-chn', 'IN', 'r-tn', 'city', 'Chennai', 'chennai', 'Asia/Kolkata', true) on conflict do nothing;
insert into regions values ('c-dxb', 'AE', 'r-dxb-e', 'city', 'Dubai', 'dubai', 'Asia/Dubai', true) on conflict do nothing;
insert into traditions (id, slug, name) values ('t-kh', 'kerala-hindu', 'Kerala Hindu') on conflict do nothing;
insert into traditions (id, slug, name) values ('t-kc', 'kerala-christian', 'Kerala Christian') on conflict do nothing;
insert into traditions (id, slug, name) values ('t-km', 'kerala-muslim', 'Kerala Muslim') on conflict do nothing;
insert into traditions (id, slug, name) values ('t-ta', 'tamil', 'Tamil') on conflict do nothing;
insert into traditions (id, slug, name) values ('t-any', 'any', 'Any or mixed') on conflict do nothing;
insert into categories (id, slug, name, kind, icon) values ('k-plan', 'event-planners', 'Event planners', 'service', 'ClipboardText') on conflict do nothing;
insert into categories (id, slug, name, kind, icon) values ('k-mua', 'makeup', 'Makeup artists', 'service', 'PaintBrush') on conflict do nothing;
insert into categories (id, slug, name, kind, icon) values ('k-photo', 'photography', 'Photographers', 'service', 'Camera') on conflict do nothing;
insert into categories (id, slug, name, kind, icon) values ('k-video', 'videography', 'Videographers', 'service', 'VideoCamera') on conflict do nothing;
insert into categories (id, slug, name, kind, icon) values ('k-decor', 'decor', 'Decor', 'service', 'FlowerLotus') on conflict do nothing;
insert into categories (id, slug, name, kind, icon) values ('k-cater', 'catering', 'Catering', 'service', 'CookingPot') on conflict do nothing;
insert into categories (id, slug, name, kind, icon) values ('k-sound', 'sound', 'Sound rental', 'equipment', 'SpeakerHifi') on conflict do nothing;
insert into categories (id, slug, name, kind, icon) values ('k-light', 'lighting', 'Lighting rental', 'equipment', 'Lightbulb') on conflict do nothing;
insert into categories (id, slug, name, kind, icon) values ('k-power', 'generators', 'Generators', 'equipment', 'Lightning') on conflict do nothing;

-- ---------- 001a_base_data.sql ----------
-- Reference data later migrations point at, so a fresh database migrates fully before seeding.
-- Same rows as src/lib/seed.ts; existing rows are left alone.
insert into traditions (id, slug, name) values
  ('t-kh','kerala-hindu','Kerala Hindu'),
  ('t-kc','kerala-christian','Kerala Christian'),
  ('t-km','kerala-muslim','Kerala Muslim'),
  ('t-ta','tamil','Tamil'),
  ('t-any','any','Any or mixed')
on conflict (id) do nothing;
insert into categories (id, slug, name, kind, icon) values
  ('k-plan','event-planners','Event planners','service','ClipboardText'),
  ('k-mua','makeup','Makeup artists','service','PaintBrush'),
  ('k-photo','photography','Photographers','service','Camera'),
  ('k-video','videography','Videographers','service','VideoCamera'),
  ('k-decor','decor','Decor','service','FlowerLotus'),
  ('k-cater','catering','Catering','service','CookingPot'),
  ('k-sound','sound','Sound rental','equipment','SpeakerHifi'),
  ('k-light','lighting','Lighting rental','equipment','Lightbulb'),
  ('k-power','generators','Generators','equipment','Lightning')
on conflict (id) do nothing;

-- ---------- 002_planner.sql ----------
-- Event planner: occasion types, checklist templates by tradition and size, customers' events.

insert into categories (id, slug, name, kind, icon) values
  ('k-mehendi', 'mehendi', 'Mehendi artists', 'service', 'HandPalm'),
  ('k-music',   'live-music', 'Live music and performers', 'service', 'MusicNotes'),
  ('k-cake',    'cakes', 'Cakes and desserts', 'service', 'Cake'),
  ('k-car',     'wedding-cars', 'Wedding cars and transport', 'service', 'Car'),
  ('k-anchor',  'anchors', 'Anchors and DJs', 'service', 'MicrophoneStage')
on conflict (id) do nothing;

create table event_types (
  id text primary key, slug text unique not null, name text not null, icon text not null, sort int not null default 0
);
insert into event_types values
  ('et-wedding','wedding','Wedding','Heart',1), ('et-engage','engagement','Engagement','Diamond',2),
  ('et-baptism','baptism','Baptism','Drop',3), ('et-birthday','birthday','Birthday','Cake',4),
  ('et-corporate','corporate','Corporate event','Briefcase',5), ('et-proposal','proposal','Proposal','Sparkle',6);

-- A template is the starting checklist for one occasion, optionally one tradition, and one size.
create table event_templates (
  id text primary key, event_type_id text not null references event_types(id) on delete cascade,
  tradition_id text references traditions(id) on delete cascade, size_tier text not null check (size_tier in ('intimate','standard'))
);
create unique index on event_templates (event_type_id, coalesce(tradition_id, ''), size_tier);
create table event_template_items (
  id serial primary key, template_id text not null references event_templates(id) on delete cascade,
  category_id text not null references categories(id) on delete restrict, sub_event text not null default 'Main event',
  label text not null, note text not null default '', budget_share int not null default 0, sort int not null default 0
);
create index on event_template_items (template_id);

insert into event_templates values
  ('tp-w-kh','et-wedding','t-kh','standard'), ('tp-w-kc','et-wedding','t-kc','standard'), ('tp-w-km','et-wedding','t-km','standard'),
  ('tp-w-any','et-wedding',null,'standard'), ('tp-w-int','et-wedding',null,'intimate'),
  ('tp-e-any','et-engage',null,'standard'), ('tp-b-any','et-baptism',null,'standard'), ('tp-bd-any','et-birthday',null,'standard'),
  ('tp-c-any','et-corporate',null,'standard'), ('tp-p-any','et-proposal',null,'intimate');

insert into event_template_items (template_id, category_id, sub_event, label, note, budget_share, sort) values
  -- Kerala Hindu wedding
  ('tp-w-kh','k-mehendi','Haldi and mehendi','Mehendi artist','Bride and close family',3,1),
  ('tp-w-kh','k-mua','Haldi and mehendi','Haldi look','Light makeup and hair',2,2),
  ('tp-w-kh','k-decor','Muhurtham','Mandapam decor','Nilavilakku, jasmine, kolam',15,3),
  ('tp-w-kh','k-mua','Muhurtham','Bridal makeup','Kasavu saree draping',8,4),
  ('tp-w-kh','k-music','Muhurtham','Nadaswaram and chenda','Live ensemble for the ceremony',5,5),
  ('tp-w-kh','k-photo','Muhurtham','Photography','Ceremony to reception',12,6),
  ('tp-w-kh','k-video','Muhurtham','Wedding film','Highlights and full ceremony',8,7),
  ('tp-w-kh','k-cater','Muhurtham','Sadya catering','Banana leaf service',25,8),
  ('tp-w-kh','k-sound','Muhurtham','Sound system','Mics for the ceremony and announcements',3,9),
  ('tp-w-kh','k-light','Reception','Reception lighting','Stage and hall lights',4,10),
  ('tp-w-kh','k-anchor','Reception','Anchor or DJ','',3,11),
  ('tp-w-kh','k-car','Reception','Wedding car','Decorated, with driver',2,12),
  ('tp-w-kh','k-power','Reception','Generator backup','For outdoor or evening events',2,13),
  -- Kerala Christian wedding
  ('tp-w-kc','k-mua','Church ceremony','Bridal makeup','Saree and veil styling',8,1),
  ('tp-w-kc','k-decor','Church ceremony','Church decor','Altar flowers and pew bows',10,2),
  ('tp-w-kc','k-sound','Church ceremony','Choir microphones and sound','Rental with technician',3,3),
  ('tp-w-kc','k-photo','Church ceremony','Photography','Church and reception',12,4),
  ('tp-w-kc','k-video','Church ceremony','Wedding film','',8,5),
  ('tp-w-kc','k-car','Church ceremony','Wedding car','Decorated, with driver',2,6),
  ('tp-w-kc','k-decor','Reception','Reception hall decor','Stage backdrop and tables',10,7),
  ('tp-w-kc','k-cater','Reception','Reception catering','Buffet or plated',25,8),
  ('tp-w-kc','k-cake','Reception','Wedding cake','Cake cutting at reception',3,9),
  ('tp-w-kc','k-light','Reception','Reception lighting','',4,10),
  ('tp-w-kc','k-anchor','Reception','Anchor or DJ','',3,11),
  ('tp-w-kc','k-power','Reception','Generator backup','',2,12),
  -- Kerala Muslim wedding
  ('tp-w-km','k-mehendi','Mehendi night','Mehendi artist','Bride and family',4,1),
  ('tp-w-km','k-music','Mehendi night','Oppana group','Traditional performance',4,2),
  ('tp-w-km','k-decor','Nikah','Nikah stage decor','Floral backdrop',12,3),
  ('tp-w-km','k-mua','Nikah','Bridal makeup','Hijab friendly styling',8,4),
  ('tp-w-km','k-photo','Nikah','Photography','Separate teams on request',12,5),
  ('tp-w-km','k-video','Nikah','Wedding film','',8,6),
  ('tp-w-km','k-cater','Reception','Biryani catering','Large batch service',25,7),
  ('tp-w-km','k-sound','Reception','Sound system','',3,8),
  ('tp-w-km','k-light','Reception','Lighting','',4,9),
  ('tp-w-km','k-car','Reception','Wedding car','',2,10),
  ('tp-w-km','k-power','Reception','Generator backup','',2,11),
  -- Any tradition, standard wedding
  ('tp-w-any','k-plan','Planning','Wedding planner','Full or day of coordination',10,1),
  ('tp-w-any','k-decor','Ceremony','Ceremony decor','',12,2),
  ('tp-w-any','k-mua','Ceremony','Bridal makeup','',8,3),
  ('tp-w-any','k-photo','Ceremony','Photography','',12,4),
  ('tp-w-any','k-video','Ceremony','Videography','',8,5),
  ('tp-w-any','k-cater','Reception','Catering','',25,6),
  ('tp-w-any','k-sound','Reception','Sound system','',3,7),
  ('tp-w-any','k-light','Reception','Lighting','',4,8),
  ('tp-w-any','k-cake','Reception','Cake','',2,9),
  -- Intimate wedding, any tradition (up to 50 guests)
  ('tp-w-int','k-plan','Main event','Day coordinator','One person runs the day',10,1),
  ('tp-w-int','k-decor','Main event','Home or small venue decor','Up to 50 guests',15,2),
  ('tp-w-int','k-mua','Main event','Bridal makeup','',10,3),
  ('tp-w-int','k-photo','Main event','Two hour candid shoot','',15,4),
  ('tp-w-int','k-cater','Main event','Catering for 20 to 50','Plated or buffet',30,5),
  ('tp-w-int','k-sound','Main event','Compact sound kit','Plug and play',3,6),
  ('tp-w-int','k-cake','Main event','Small cake','',3,7),
  -- Engagement
  ('tp-e-any','k-decor','Main event','Ring ceremony decor','',20,1), ('tp-e-any','k-mua','Main event','Makeup','',10,2),
  ('tp-e-any','k-photo','Main event','Photography','',20,3), ('tp-e-any','k-cater','Main event','Catering','',35,4),
  ('tp-e-any','k-sound','Main event','Sound system','',5,5),
  -- Baptism
  ('tp-b-any','k-decor','Main event','Church and hall decor','',20,1), ('tp-b-any','k-photo','Main event','Photography','',20,2),
  ('tp-b-any','k-cater','Main event','Catering','',40,3), ('tp-b-any','k-cake','Main event','Cake','',10,4),
  -- Birthday
  ('tp-bd-any','k-decor','Main event','Theme decor and balloons','',25,1), ('tp-bd-any','k-cake','Main event','Custom cake','',15,2),
  ('tp-bd-any','k-anchor','Main event','Anchor, DJ or entertainer','',15,3), ('tp-bd-any','k-photo','Main event','Photography','',15,4),
  ('tp-bd-any','k-cater','Main event','Catering','',25,5), ('tp-bd-any','k-light','Main event','Party lights','',5,6),
  -- Corporate
  ('tp-c-any','k-plan','Main event','Event manager','',15,1), ('tp-c-any','k-sound','Main event','Sound and microphones','',10,2),
  ('tp-c-any','k-light','Main event','Stage lighting','',10,3), ('tp-c-any','k-anchor','Main event','Anchor or host','',10,4),
  ('tp-c-any','k-photo','Main event','Photography','',10,5), ('tp-c-any','k-cater','Main event','Catering','',35,6),
  ('tp-c-any','k-power','Main event','Generator backup','',10,7),
  -- Proposal
  ('tp-p-any','k-decor','Main event','Proposal setup','Flowers, candles, signage',45,1),
  ('tp-p-any','k-photo','Main event','Hidden photographer','',35,2), ('tp-p-any','k-music','Main event','Live musician','',20,3);

create table events (
  id text primary key default ('ev-' || substr(gen_random_uuid()::text,1,12)),
  owner_id uuid not null references users(id) on delete cascade,
  event_type_id text not null references event_types(id) on delete restrict,
  tradition_id text references traditions(id) on delete set null,
  city_id text not null references regions(id) on delete restrict,
  title text not null, guest_count int check (guest_count between 1 and 20000),
  size_tier text not null check (size_tier in ('intimate','standard')),
  budget_minor bigint check (budget_minor >= 0), currency char(3) not null,
  event_date date, created_at timestamptz not null default now()
);
create index on events (owner_id);

create table event_items (
  id text primary key default ('ei-' || substr(gen_random_uuid()::text,1,12)),
  event_id text not null references events(id) on delete cascade,
  category_id text not null references categories(id) on delete restrict,
  sub_event text not null, label text not null, note text not null default '',
  budget_share int not null default 0,
  status text not null default 'todo' check (status in ('todo','shortlisted','booked','skipped')),
  sort int not null default 0
);
create index on event_items (event_id, sort);

create table shortlist (
  event_item_id text not null references event_items(id) on delete cascade,
  item_kind text not null check (item_kind in ('service','equipment')), item_id text not null,
  created_at timestamptz not null default now(), primary key (event_item_id, item_kind, item_id)
);

alter table bookings add column event_item_id text references event_items(id) on delete set null;
create index on bookings (event_item_id);

-- ---------- 003_admin.sql ----------
-- Admin area: vendor review notes and an audit trail of admin actions.
alter table vendors add column verified_at timestamptz, add column verified_by uuid references users(id) on delete set null,
  add column review_note text not null default '';
create table admin_log (
  id bigserial primary key, admin_id uuid references users(id) on delete set null,
  action text not null, target text not null, detail jsonb not null default '{}', created_at timestamptz not null default now()
);
create index on admin_log (created_at desc);

-- ---------- 004_media.sql ----------
-- Photos for vendor portfolios and listings. Files live in object storage; this table holds the keys.
create table media (
  id text primary key default ('m-' || substr(gen_random_uuid()::text,1,12)),
  vendor_id text not null references vendors(id) on delete cascade,
  owner_kind text not null check (owner_kind in ('vendor','service','equipment')),
  owner_id text not null, storage_key text unique not null,
  width int not null, height int not null, bytes int not null, alt text not null default '',
  sort int not null default 0, created_at timestamptz not null default now()
);
create index on media (owner_kind, owner_id, sort);
create index on media (vendor_id);

-- ---------- 005_notifications.sql ----------
-- Outbox for emails (and later WhatsApp/SMS). Rows are written first, then sent; failures are retried.
create table notifications (
  id bigserial primary key,
  channel text not null default 'email' check (channel in ('email','whatsapp','sms')),
  to_address text not null, subject text not null, body text not null,
  kind text not null, booking_id text references bookings(id) on delete set null,
  status text not null default 'pending' check (status in ('pending','sent','failed')),
  attempts int not null default 0, last_error text, next_try_at timestamptz not null default now(),
  created_at timestamptz not null default now(), sent_at timestamptz
);
create index on notifications (status, next_try_at);
-- One message per booking event and recipient, so a double click or retry never sends twice.
create unique index on notifications (kind, booking_id, to_address) where booking_id is not null;
alter table bookings add column cancelled_at timestamptz;

-- ---------- 006_all_events.sql ----------
-- Any kind of event: grouped event types, more vendor categories, more traditions, and a checklist for every type.

alter table event_types add column grp text not null default 'Celebrations';
alter table event_types add column description text not null default '';
alter table event_types add column active boolean not null default true;
update event_types set grp = 'Weddings and family' where id in ('et-wedding','et-engage','et-proposal');
update event_types set grp = 'Religious and cultural' where id = 'et-baptism';
update event_types set grp = 'Parties and celebrations' where id = 'et-birthday';
update event_types set grp = 'Business and professional' where id = 'et-corporate';
alter table traditions add column active boolean not null default true;
alter table categories add column active boolean not null default true;

-- Vendor categories needed beyond weddings
insert into categories (id, slug, name, kind, icon) values
  ('k-venue',    'venues', 'Venues and halls', 'service', 'Buildings'),
  ('k-priest',   'priests-officiants', 'Priests and officiants', 'service', 'HandsPraying'),
  ('k-florist',  'florists', 'Florists', 'service', 'Flower'),
  ('k-print',    'invitations-printing', 'Invitations and printing', 'service', 'Envelope'),
  ('k-gifts',    'gifts-favours', 'Gifts and favours', 'service', 'Gift'),
  ('k-kids',     'kids-entertainment', 'Kids entertainment', 'service', 'Balloon'),
  ('k-security', 'security-staff', 'Security and crowd staff', 'service', 'ShieldCheck'),
  ('k-hosts',    'hosts-ushers', 'Hosts, ushers and helpers', 'service', 'UsersThree'),
  ('k-clean',    'cleaning', 'Cleaning', 'service', 'Broom'),
  ('k-brand',    'branding-signage', 'Branding and signage', 'service', 'Flag'),
  ('k-stream',   'live-streaming', 'Live streaming', 'service', 'Broadcast'),
  ('k-av',       'av-led-screens', 'Projectors and LED screens', 'equipment', 'Monitor'),
  ('k-stage',    'stage-truss', 'Stage and truss', 'equipment', 'Cube'),
  ('k-tent',     'tents-canopies', 'Tents and canopies', 'equipment', 'Tent'),
  ('k-furn',     'furniture-rental', 'Furniture rental', 'equipment', 'Armchair'),
  ('k-cool',     'fans-coolers', 'Fans, coolers and AC', 'equipment', 'Fan')
on conflict (id) do nothing;

-- More traditions (used to suggest, never to restrict)
insert into traditions (id, slug, name) values
  ('t-hn',  'north-indian-hindu', 'North Indian Hindu'),
  ('t-sik', 'sikh', 'Sikh'),
  ('t-chr', 'christian', 'Christian (general)'),
  ('t-mus', 'muslim', 'Muslim (general)'),
  ('t-tb',  'tamil-brahmin', 'Tamil Brahmin'),
  ('t-sec', 'secular', 'Non-religious')
on conflict (id) do nothing;

-- Event types across every part of life
insert into event_types (id, slug, name, icon, sort, grp) values
  ('et-reception',   'reception', 'Wedding reception', 'Champagne', 7, 'Weddings and family'),
  ('et-anniv',       'anniversary', 'Anniversary', 'Heart', 8, 'Weddings and family'),
  ('et-babyshower',  'baby-shower', 'Baby shower', 'Baby', 9, 'Weddings and family'),
  ('et-naming',      'naming-ceremony', 'Naming ceremony', 'Baby', 10, 'Weddings and family'),
  ('et-housewarm',   'housewarming', 'Housewarming', 'House', 11, 'Weddings and family'),
  ('et-retire',      'retirement', 'Retirement party', 'Coffee', 12, 'Weddings and family'),
  ('et-memorial',    'memorial', 'Memorial or remembrance', 'Flower', 13, 'Weddings and family'),
  ('et-communion',   'first-communion', 'First Holy Communion', 'Church', 20, 'Religious and cultural'),
  ('et-puja',        'puja', 'Puja or homam', 'FlowerLotus', 21, 'Religious and cultural'),
  ('et-iftar',       'iftar', 'Iftar or Eid gathering', 'MoonStars', 22, 'Religious and cultural'),
  ('et-festival',    'festival', 'Festival celebration (Onam, Diwali, Christmas)', 'Sparkle', 23, 'Religious and cultural'),
  ('et-temple',      'temple-church-feast', 'Temple, church or mosque event', 'Bank', 24, 'Religious and cultural'),
  ('et-kids',        'kids-party', 'Kids party', 'Balloon', 30, 'Parties and celebrations'),
  ('et-reunion',     'reunion', 'Reunion', 'UsersThree', 31, 'Parties and celebrations'),
  ('et-dinner',      'private-dinner', 'Private dinner', 'ForkKnife', 32, 'Parties and celebrations'),
  ('et-newyear',     'new-year-party', 'New Year or theme party', 'Confetti', 33, 'Parties and celebrations'),
  ('et-conf',        'conference', 'Conference or seminar', 'Presentation', 40, 'Business and professional'),
  ('et-launch',      'product-launch', 'Product launch', 'RocketLaunch', 41, 'Business and professional'),
  ('et-expo',        'exhibition', 'Exhibition or trade show', 'Storefront', 42, 'Business and professional'),
  ('et-offsite',     'team-offsite', 'Team outing or offsite', 'Mountains', 43, 'Business and professional'),
  ('et-awards',      'awards-night', 'Awards night or gala', 'Trophy', 44, 'Business and professional'),
  ('et-opening',     'shop-opening', 'Shop or office opening', 'Storefront', 45, 'Business and professional'),
  ('et-college',     'college-fest', 'College or school event', 'GraduationCap', 50, 'Community and public'),
  ('et-sports',      'sports-event', 'Sports event or tournament', 'SoccerBall', 51, 'Community and public'),
  ('et-concert',     'concert', 'Concert or live show', 'MusicNotes', 52, 'Community and public'),
  ('et-charity',     'charity', 'Charity or fundraiser', 'HandHeart', 53, 'Community and public'),
  ('et-community',   'community-gathering', 'Community or association meeting', 'UsersThree', 54, 'Community and public'),
  ('et-other',       'other', 'Something else', 'Sparkle', 99, 'Something else')
on conflict (id) do nothing;

insert into event_templates (id, event_type_id, tradition_id, size_tier) values
  ('tp-reception','et-reception',null,'standard'), ('tp-anniv','et-anniv',null,'standard'), ('tp-babyshower','et-babyshower',null,'standard'),
  ('tp-naming','et-naming',null,'standard'), ('tp-housewarm','et-housewarm',null,'standard'), ('tp-retire','et-retire',null,'standard'),
  ('tp-memorial','et-memorial',null,'standard'), ('tp-communion','et-communion',null,'standard'), ('tp-puja','et-puja',null,'standard'),
  ('tp-iftar','et-iftar',null,'standard'), ('tp-festival','et-festival',null,'standard'), ('tp-temple','et-temple',null,'standard'),
  ('tp-kids','et-kids',null,'standard'), ('tp-reunion','et-reunion',null,'standard'), ('tp-dinner','et-dinner',null,'intimate'),
  ('tp-newyear','et-newyear',null,'standard'), ('tp-conf','et-conf',null,'standard'), ('tp-launch','et-launch',null,'standard'),
  ('tp-expo','et-expo',null,'standard'), ('tp-offsite','et-offsite',null,'standard'), ('tp-awards','et-awards',null,'standard'),
  ('tp-opening','et-opening',null,'standard'), ('tp-college','et-college',null,'standard'), ('tp-sports','et-sports',null,'standard'),
  ('tp-concert','et-concert',null,'standard'), ('tp-charity','et-charity',null,'standard'), ('tp-community','et-community',null,'standard'),
  ('tp-other','et-other',null,'standard'), ('tp-bd-int','et-birthday',null,'intimate')
on conflict do nothing;

insert into event_template_items (template_id, category_id, sub_event, label, note, budget_share, sort) values
  ('tp-reception','k-venue','Reception','Venue or hall','',20,1), ('tp-reception','k-decor','Reception','Stage and hall decor','',15,2), ('tp-reception','k-cater','Reception','Catering','',35,3), ('tp-reception','k-photo','Reception','Photography','',10,4), ('tp-reception','k-anchor','Reception','Anchor or DJ','',5,5), ('tp-reception','k-light','Reception','Lighting','',5,6), ('tp-reception','k-sound','Reception','Sound system','',5,7), ('tp-reception','k-cake','Reception','Cake','',5,8),
  ('tp-anniv','k-venue','Main event','Venue or restaurant','',25,1), ('tp-anniv','k-decor','Main event','Decor','',15,2), ('tp-anniv','k-cater','Main event','Catering','',35,3), ('tp-anniv','k-cake','Main event','Cake','',10,4), ('tp-anniv','k-photo','Main event','Photography','',15,5),
  ('tp-babyshower','k-decor','Main event','Theme decor','',25,1), ('tp-babyshower','k-cater','Main event','Food and snacks','',35,2), ('tp-babyshower','k-cake','Main event','Cake','',10,3), ('tp-babyshower','k-photo','Main event','Photography','',15,4), ('tp-babyshower','k-gifts','Main event','Return gifts','',15,5),
  ('tp-naming','k-priest','Ceremony','Priest or officiant','',10,1), ('tp-naming','k-decor','Ceremony','Decor','',20,2), ('tp-naming','k-cater','Ceremony','Catering','',45,3), ('tp-naming','k-photo','Ceremony','Photography','',15,4), ('tp-naming','k-gifts','Ceremony','Return gifts','',10,5),
  ('tp-housewarm','k-priest','Ceremony','Priest for the blessing or puja','',10,1), ('tp-housewarm','k-decor','Ceremony','Flowers and entrance decor','',15,2), ('tp-housewarm','k-cater','Ceremony','Catering','',50,3), ('tp-housewarm','k-tent','Ceremony','Canopy for guests','',10,4), ('tp-housewarm','k-photo','Ceremony','Photography','',10,5), ('tp-housewarm','k-cool','Ceremony','Fans or coolers','',5,6),
  ('tp-retire','k-venue','Main event','Venue','',25,1), ('tp-retire','k-cater','Main event','Catering','',40,2), ('tp-retire','k-anchor','Main event','Host','',10,3), ('tp-retire','k-sound','Main event','Sound and mic','',5,4), ('tp-retire','k-photo','Main event','Photography','',10,5), ('tp-retire','k-gifts','Main event','Memento','',10,6),
  ('tp-memorial','k-venue','Service','Hall or venue','',25,1), ('tp-memorial','k-florist','Service','Flowers','',15,2), ('tp-memorial','k-tent','Service','Canopy and seating','',15,3), ('tp-memorial','k-cater','Service','Simple meal','',35,4), ('tp-memorial','k-sound','Service','Sound and mic','',10,5),
  ('tp-communion','k-decor','Church','Church decor','',15,1), ('tp-communion','k-photo','Church','Photography','',15,2), ('tp-communion','k-venue','Celebration','Hall','',20,3), ('tp-communion','k-cater','Celebration','Catering','',40,4), ('tp-communion','k-cake','Celebration','Cake','',10,5),
  ('tp-puja','k-priest','Puja','Priest','',20,1), ('tp-puja','k-florist','Puja','Flowers and garlands','',15,2), ('tp-puja','k-cater','Puja','Prasadam and meal','',40,3), ('tp-puja','k-tent','Puja','Canopy','',10,4), ('tp-puja','k-sound','Puja','Sound for chanting','',5,5), ('tp-puja','k-photo','Puja','Photography','',10,6),
  ('tp-iftar','k-venue','Gathering','Venue or hall','',20,1), ('tp-iftar','k-cater','Gathering','Iftar food','',55,2), ('tp-iftar','k-decor','Gathering','Lights and decor','',10,3), ('tp-iftar','k-furn','Gathering','Seating','',10,4), ('tp-iftar','k-sound','Gathering','Sound','',5,5),
  ('tp-festival','k-decor','Celebration','Festive decor','Pookalam, lamps or tree',20,1), ('tp-festival','k-cater','Celebration','Festive meal','Sadya, sweets or dinner',40,2), ('tp-festival','k-music','Celebration','Performers','',15,3), ('tp-festival','k-sound','Celebration','Sound','',5,4), ('tp-festival','k-light','Celebration','Lights','',10,5), ('tp-festival','k-photo','Celebration','Photography','',10,6),
  ('tp-temple','k-tent','Event','Pandal or canopy','',20,1), ('tp-temple','k-sound','Event','Sound system','',10,2), ('tp-temple','k-light','Event','Lighting','',10,3), ('tp-temple','k-power','Event','Generator','',10,4), ('tp-temple','k-cater','Event','Food service','',30,5), ('tp-temple','k-security','Event','Crowd staff','',10,6), ('tp-temple','k-clean','Event','Cleaning','',10,7),
  ('tp-kids','k-decor','Party','Theme decor and balloons','',25,1), ('tp-kids','k-kids','Party','Magician, games or mascot','',20,2), ('tp-kids','k-cake','Party','Cake','',15,3), ('tp-kids','k-cater','Party','Snacks','',25,4), ('tp-kids','k-gifts','Party','Return gifts','',10,5), ('tp-kids','k-photo','Party','Photography','',5,6),
  ('tp-reunion','k-venue','Main event','Venue','',30,1), ('tp-reunion','k-cater','Main event','Catering','',40,2), ('tp-reunion','k-sound','Main event','Sound and mic','',5,3), ('tp-reunion','k-anchor','Main event','Host or DJ','',10,4), ('tp-reunion','k-photo','Main event','Photography','',10,5), ('tp-reunion','k-print','Main event','Name tags and banners','',5,6),
  ('tp-dinner','k-venue','Dinner','Private room or home chef','',35,1), ('tp-dinner','k-cater','Dinner','Menu','',40,2), ('tp-dinner','k-decor','Dinner','Table styling','',15,3), ('tp-dinner','k-music','Dinner','Live musician','',10,4),
  ('tp-newyear','k-venue','Party','Venue','',25,1), ('tp-newyear','k-anchor','Party','DJ','',15,2), ('tp-newyear','k-sound','Party','Sound system','',10,3), ('tp-newyear','k-light','Party','Party lights','',10,4), ('tp-newyear','k-cater','Party','Food and drinks','',30,5), ('tp-newyear','k-security','Party','Security','',10,6),
  ('tp-conf','k-venue','Conference','Venue and rooms','',25,1), ('tp-conf','k-av','Conference','Projectors and LED screen','',10,2), ('tp-conf','k-sound','Conference','Mics and sound','',8,3), ('tp-conf','k-stage','Conference','Stage','',7,4), ('tp-conf','k-cater','Conference','Tea, lunch and snacks','',25,5), ('tp-conf','k-hosts','Conference','Registration desk and ushers','',5,6), ('tp-conf','k-brand','Conference','Banners and signage','',5,7), ('tp-conf','k-stream','Conference','Live streaming','',5,8), ('tp-conf','k-photo','Conference','Photography','',5,9), ('tp-conf','k-power','Conference','Generator backup','',5,10),
  ('tp-launch','k-venue','Launch','Venue','',20,1), ('tp-launch','k-stage','Launch','Stage and backdrop','',15,2), ('tp-launch','k-av','Launch','LED screen','',15,3), ('tp-launch','k-light','Launch','Show lighting','',10,4), ('tp-launch','k-anchor','Launch','Host','',5,5), ('tp-launch','k-brand','Launch','Branding','',10,6), ('tp-launch','k-cater','Launch','Catering','',15,7), ('tp-launch','k-video','Launch','Video coverage','',10,8),
  ('tp-expo','k-tent','Exhibition','Stalls or hangar','',25,1), ('tp-expo','k-furn','Exhibition','Furniture','',10,2), ('tp-expo','k-brand','Exhibition','Signage','',10,3), ('tp-expo','k-power','Exhibition','Power and generators','',10,4), ('tp-expo','k-light','Exhibition','Lighting','',10,5), ('tp-expo','k-security','Exhibition','Security','',10,6), ('tp-expo','k-clean','Exhibition','Cleaning','',5,7), ('tp-expo','k-cater','Exhibition','Food court','',15,8), ('tp-expo','k-hosts','Exhibition','Registration staff','',5,9),
  ('tp-offsite','k-venue','Outing','Resort or venue','',40,1), ('tp-offsite','k-cater','Outing','Meals','',30,2), ('tp-offsite','k-car','Outing','Transport','',15,3), ('tp-offsite','k-anchor','Outing','Games host','',10,4), ('tp-offsite','k-photo','Outing','Photography','',5,5),
  ('tp-awards','k-venue','Gala','Venue','',25,1), ('tp-awards','k-stage','Gala','Stage','',10,2), ('tp-awards','k-av','Gala','LED screen','',10,3), ('tp-awards','k-light','Gala','Show lighting','',10,4), ('tp-awards','k-anchor','Gala','Host','',5,5), ('tp-awards','k-gifts','Gala','Trophies','',10,6), ('tp-awards','k-cater','Gala','Dinner','',25,7), ('tp-awards','k-photo','Gala','Photography','',5,8),
  ('tp-opening','k-priest','Opening','Blessing or ribbon cutting','',10,1), ('tp-opening','k-decor','Opening','Entrance decor and balloons','',20,2), ('tp-opening','k-sound','Opening','Sound and mic','',10,3), ('tp-opening','k-brand','Opening','Banners','',15,4), ('tp-opening','k-cater','Opening','Snacks and sweets','',30,5), ('tp-opening','k-photo','Opening','Photography','',15,6),
  ('tp-college','k-stage','Event','Stage','',15,1), ('tp-college','k-sound','Event','Sound system','',15,2), ('tp-college','k-light','Event','Lighting','',10,3), ('tp-college','k-av','Event','LED screen','',10,4), ('tp-college','k-anchor','Event','Host or DJ','',10,5), ('tp-college','k-cater','Event','Food stalls','',20,6), ('tp-college','k-security','Event','Security','',10,7), ('tp-college','k-power','Event','Generator','',10,8),
  ('tp-sports','k-tent','Event','Canopies','',20,1), ('tp-sports','k-sound','Event','Public address','',10,2), ('tp-sports','k-furn','Event','Seating','',15,3), ('tp-sports','k-cater','Event','Refreshments','',20,4), ('tp-sports','k-gifts','Event','Trophies and medals','',15,5), ('tp-sports','k-security','Event','First aid and security','',10,6), ('tp-sports','k-photo','Event','Photography','',10,7),
  ('tp-concert','k-stage','Show','Stage and truss','',20,1), ('tp-concert','k-sound','Show','Concert sound','',20,2), ('tp-concert','k-light','Show','Show lighting','',15,3), ('tp-concert','k-av','Show','LED screens','',10,4), ('tp-concert','k-power','Show','Generators','',10,5), ('tp-concert','k-security','Show','Security and crowd control','',15,6), ('tp-concert','k-clean','Show','Cleaning','',5,7), ('tp-concert','k-stream','Show','Live streaming','',5,8),
  ('tp-charity','k-venue','Event','Venue','',25,1), ('tp-charity','k-cater','Event','Catering','',30,2), ('tp-charity','k-anchor','Event','Host','',10,3), ('tp-charity','k-sound','Event','Sound and mic','',10,4), ('tp-charity','k-brand','Event','Banners','',10,5), ('tp-charity','k-photo','Event','Photography','',15,6),
  ('tp-community','k-venue','Meeting','Hall','',30,1), ('tp-community','k-sound','Meeting','Mics and sound','',15,2), ('tp-community','k-furn','Meeting','Chairs and tables','',15,3), ('tp-community','k-cater','Meeting','Tea and snacks','',30,4), ('tp-community','k-av','Meeting','Projector','',10,5),
  ('tp-other','k-venue','Main event','Venue','Add or remove anything',30,1), ('tp-other','k-cater','Main event','Food and drinks','',35,2), ('tp-other','k-decor','Main event','Decor','',15,3), ('tp-other','k-sound','Main event','Sound','',10,4), ('tp-other','k-photo','Main event','Photography','',10,5),
  ('tp-bd-int','k-decor','Party','Home decor and balloons','',30,1), ('tp-bd-int','k-cake','Party','Cake','',20,2), ('tp-bd-int','k-cater','Party','Food for a small group','',40,3), ('tp-bd-int','k-photo','Party','One hour photo session','',10,4);

-- ---------- 007_reviews.sql ----------
-- Reviews: one per real booking, only after the event date, only by that booking's customer.
create table reviews (
  id text primary key default ('r-' || substr(gen_random_uuid()::text,1,12)),
  booking_id text unique not null references bookings(id) on delete cascade,
  vendor_id text not null references vendors(id) on delete cascade,
  customer_id uuid references users(id) on delete set null,
  author_name text not null,               -- first name and initial, shown publicly
  rating int not null check (rating between 1 and 5),
  body text not null default '' check (length(body) <= 1000),
  vendor_reply text check (length(vendor_reply) <= 600), replied_at timestamptz,
  hidden boolean not null default false, hidden_reason text,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create index on reviews (vendor_id, created_at desc);

-- Keep each vendor's average and count in step with its visible reviews.
create function refresh_vendor_rating() returns trigger language plpgsql as $$
declare v text := coalesce(new.vendor_id, old.vendor_id);
begin
  update vendors set
    rating_avg = coalesce((select round(avg(rating)::numeric, 2) from reviews where vendor_id = v and not hidden), 0),
    rating_count = (select count(*) from reviews where vendor_id = v and not hidden)
  where id = v;
  return null;
end $$;
create trigger reviews_rating after insert or update or delete on reviews for each row execute function refresh_vendor_rating();

-- Seed vendors had made-up rating numbers; from now on ratings only come from real reviews.
update vendors set rating_avg = 0, rating_count = 0;

-- ---------- 008_availability.sql ----------
-- Days a vendor is not taking work (holidays, private events). New booking requests on these days are refused,
-- for services and gear alike. Booking and blocking both lock the vendor row, so the two cannot race.
create table vendor_blocks (
  id bigserial primary key,
  vendor_id text not null references vendors(id) on delete cascade,
  period daterange not null check (not isempty(period)),
  note text not null default '' check (length(note) <= 120),
  created_at timestamptz not null default now()
);
create index on vendor_blocks using gist (vendor_id, period);

-- ---------- record applied migrations, so `npm run db:migrate` skips them later ----------
insert into schema_migrations (name) values ('001_init.sql'), ('001a_base_data.sql'), ('002_planner.sql'), ('003_admin.sql'), ('004_media.sql'), ('005_notifications.sql'), ('006_all_events.sql'), ('007_reviews.sql'), ('008_availability.sql') on conflict do nothing;

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
