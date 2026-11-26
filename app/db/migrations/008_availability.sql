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
