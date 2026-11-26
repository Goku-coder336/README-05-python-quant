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
