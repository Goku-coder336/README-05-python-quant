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
