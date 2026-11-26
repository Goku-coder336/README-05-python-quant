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
