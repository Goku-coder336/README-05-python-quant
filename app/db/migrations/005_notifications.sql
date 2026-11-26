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
