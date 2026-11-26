-- Admin area: vendor review notes and an audit trail of admin actions.
alter table vendors add column verified_at timestamptz, add column verified_by uuid references users(id) on delete set null,
  add column review_note text not null default '';
create table admin_log (
  id bigserial primary key, admin_id uuid references users(id) on delete set null,
  action text not null, target text not null, detail jsonb not null default '{}', created_at timestamptz not null default now()
);
create index on admin_log (created_at desc);
