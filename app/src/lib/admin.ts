import crypto from "node:crypto";
import { redirect, notFound } from "next/navigation";
import { currentUser, type User } from "./auth";
import { one, pool, q } from "./db";

/** Every admin page and action calls this first. Non-admins get a plain 404, so the area is not advertised. */
export async function requireAdmin(next = "/admin"): Promise<User> {
  const u = await currentUser();
  if (!u) redirect(`/signin?next=${encodeURIComponent(next)}`);
  if (u.role !== "admin") notFound();
  return u;
}

async function log(adminId: string, action: string, target: string, detail: Record<string, unknown> = {}) {
  await pool.query(`insert into admin_log (admin_id, action, target, detail) values ($1,$2,$3,$4)`, [adminId, action, target, detail]);
}

export async function overview() {
  return (await one<{ vendors: number; pending: number; customers: number; events: number; bookings: number; waitlist: number }>(`select
    (select count(*)::int from vendors) as vendors, (select count(*)::int from vendors where verification = 'pending') as pending,
    (select count(*)::int from users) as customers, (select count(*)::int from events) as events,
    (select count(*)::int from bookings) as bookings, (select count(*)::int from waitlist) as waitlist`))!;
}

export type AdminVendor = { id: string; handle: string; businessName: string; phone: string; city: string; verification: "pending" | "verified";
  ownerEmail: string | null; listings: number; bookings: number; createdAt: string; reviewNote: string; bio: string };
export async function adminVendors(filter: "pending" | "verified" | "all") {
  return q<AdminVendor>(`select v.id, v.handle, v.business_name as "businessName", v.phone, r.name as city, v.verification, u.email as "ownerEmail",
      (select count(*)::int from services s where s.vendor_id = v.id) + (select count(*)::int from equipment e where e.vendor_id = v.id) as listings,
      (select count(*)::int from bookings b where b.vendor_id = v.id) as bookings, v.created_at as "createdAt", v.review_note as "reviewNote", v.bio
    from vendors v join regions r on r.id = v.base_region_id left join users u on u.id = v.owner_id
    where ($1 = 'all' or v.verification = $1) order by v.verification = 'pending' desc, v.created_at desc`, [filter]);
}
export async function setVerification(adminId: string, vendorId: string, verified: boolean, note: string) {
  await pool.query(`update vendors set verification = $2, verified_at = case when $2 = 'verified' then now() end,
    verified_by = case when $2 = 'verified' then $3::uuid end, review_note = $4 where id = $1`, [vendorId, verified ? "verified" : "pending", adminId, note]);
  await log(adminId, verified ? "vendor.verify" : "vendor.unverify", vendorId, { note });
}

export async function waitlistByCity() {
  return q<{ city: string; customers: number; vendors: number; total: number }>(`select city,
      count(*) filter (where role = 'customer')::int as customers, count(*) filter (where role = 'vendor')::int as vendors, count(*)::int as total
    from waitlist group by city order by total desc, city`);
}
export const waitlistRows = () => q<{ email: string; role: string; city: string; createdAt: string }>(`select email, role, city, created_at as "createdAt" from waitlist order by created_at desc`);

export type TemplateRow = { id: string; eventType: string; tradition: string | null; sizeTier: string; items: number };
export const templates = () => q<TemplateRow>(`select t.id, et.name as "eventType", tr.name as tradition, t.size_tier as "sizeTier",
    (select count(*)::int from event_template_items i where i.template_id = t.id) as items
  from event_templates t join event_types et on et.id = t.event_type_id left join traditions tr on tr.id = t.tradition_id order by et.sort, tr.name nulls last, t.size_tier`);
export const template = (id: string) => one<TemplateRow>(`select t.id, et.name as "eventType", tr.name as tradition, t.size_tier as "sizeTier", 0 as items
  from event_templates t join event_types et on et.id = t.event_type_id left join traditions tr on tr.id = t.tradition_id where t.id = $1`, [id]);
export type TemplateItem = { id: number; categoryId: string; subEvent: string; label: string; note: string; budgetShare: number; sort: number };
export const templateItems = (id: string) => q<TemplateItem>(`select id, category_id as "categoryId", sub_event as "subEvent", label, note,
  budget_share as "budgetShare", sort from event_template_items where template_id = $1 order by sort, id`, [id]);

export async function saveTemplateItem(adminId: string, templateId: string, i: { id?: number; categoryId: string; subEvent: string; label: string; note: string; budgetShare: number; sort: number }) {
  if (i.id) await pool.query(`update event_template_items set category_id=$3, sub_event=$4, label=$5, note=$6, budget_share=$7, sort=$8 where id=$1 and template_id=$2`,
    [i.id, templateId, i.categoryId, i.subEvent, i.label, i.note, i.budgetShare, i.sort]);
  else await pool.query(`insert into event_template_items (template_id, category_id, sub_event, label, note, budget_share, sort) values ($1,$2,$3,$4,$5,$6,$7)`,
    [templateId, i.categoryId, i.subEvent, i.label, i.note, i.budgetShare, i.sort]);
  await log(adminId, i.id ? "template.item.update" : "template.item.add", templateId, i);
}
export async function deleteTemplateItem(adminId: string, templateId: string, itemId: number) {
  await pool.query(`delete from event_template_items where id = $1 and template_id = $2`, [itemId, templateId]);
  await log(adminId, "template.item.delete", templateId, { itemId });
}
export const recentLog = () => q<{ action: string; target: string; email: string | null; createdAt: string }>(`select l.action, l.target, u.email, l.created_at as "createdAt"
  from admin_log l left join users u on u.id = l.admin_id order by l.created_at desc limit 15`);

// ---------- catalogue: event types, categories, traditions, new checklists ----------
const slugify = (s: string) => s.toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 40);
export type AdminEventType = { id: string; name: string; grp: string; icon: string; active: boolean; templates: number; plans: number };
export const adminEventTypes = () => q<AdminEventType>(`select et.id, et.name, et.grp, et.icon, et.active,
  (select count(*)::int from event_templates t where t.event_type_id = et.id) as templates, (select count(*)::int from events e where e.event_type_id = et.id) as plans
  from event_types et order by et.grp, et.sort, et.name`);
export const adminCategories = () => q<{ id: string; name: string; kind: string; icon: string; active: boolean; listings: number }>(`select k.id, k.name, k.kind, k.icon, k.active,
  (select count(*)::int from services s where s.category_id = k.id) + (select count(*)::int from equipment e where e.category_id = k.id) as listings from categories k order by k.kind desc, k.name`);
export const adminTraditions = () => q<{ id: string; name: string; active: boolean }>(`select id, name, active from traditions order by name`);

export async function createEventType(adminId: string, i: { name: string; grp: string; icon: string }) {
  const slug = slugify(i.name); if (!slug) return { error: "Enter a name." };
  const r = await one<{ id: string }>(`insert into event_types (id, slug, name, icon, grp, sort) values ($1,$2,$3,$4,$5, coalesce((select max(sort)+1 from event_types), 1))
    on conflict do nothing returning id`, [`et-${slug}`, slug, i.name, i.icon, i.grp]);
  if (!r) return { error: "An event type with that name already exists." };
  // Every new type starts with a simple checklist so customers never see an empty plan.
  const tpl = `tp-${slug}`;
  await pool.query(`insert into event_templates values ($1,$2,null,'standard') on conflict do nothing`, [tpl, r.id]);
  await pool.query(`insert into event_template_items (template_id, category_id, sub_event, label, budget_share, sort) values
    ($1,'k-venue','Main event','Venue',30,1), ($1,'k-cater','Main event','Food and drinks',35,2), ($1,'k-decor','Main event','Decor',15,3), ($1,'k-sound','Main event','Sound',10,4), ($1,'k-photo','Main event','Photography',10,5)`, [tpl]);
  await log(adminId, "event_type.create", r.id, i);
  return { id: r.id, templateId: tpl };
}

export async function createCategory(adminId: string, i: { name: string; kind: "service" | "equipment"; icon: string }) {
  const slug = slugify(i.name); if (!slug) return { error: "Enter a name." };
  const r = await one<{ id: string }>(`insert into categories (id, slug, name, kind, icon) values ($1,$2,$3,$4,$5) on conflict do nothing returning id`, [`k-${slug}`, slug, i.name, i.kind, i.icon]);
  if (!r) return { error: "A category with that name already exists." };
  await log(adminId, "category.create", r.id, i); return { id: r.id };
}

export async function createTradition(adminId: string, name: string) {
  const slug = slugify(name); if (!slug) return { error: "Enter a name." };
  const r = await one<{ id: string }>(`insert into traditions (id, slug, name) values ($1,$2,$3) on conflict do nothing returning id`, [`t-${slug}`, slug, name]);
  if (!r) return { error: "That tradition already exists." };
  await log(adminId, "tradition.create", r.id, { name }); return { id: r.id };
}

const TABLES = { event_type: "event_types", category: "categories", tradition: "traditions" } as const;
export async function setActive(adminId: string, what: keyof typeof TABLES, id: string, active: boolean) {
  await pool.query(`update ${TABLES[what]} set active = $2 where id = $1`, [id, active]);
  await log(adminId, `${what}.${active ? "show" : "hide"}`, id);
}

/** New checklist for an occasion + tradition + size, optionally copied from an existing checklist. */
export async function createTemplate(adminId: string, i: { eventTypeId: string; traditionId: string | null; sizeTier: "intimate" | "standard"; copyFrom: string | null }) {
  const id = `tp-${crypto.randomUUID().slice(0, 8)}`;
  const r = await pool.query(`insert into event_templates values ($1,$2,$3,$4) on conflict do nothing`, [id, i.eventTypeId, i.traditionId, i.sizeTier]);
  if (!r.rowCount) return { error: "A checklist for that occasion, tradition and size already exists. Edit that one instead." };
  if (i.copyFrom) await pool.query(`insert into event_template_items (template_id, category_id, sub_event, label, note, budget_share, sort)
    select $1, category_id, sub_event, label, note, budget_share, sort from event_template_items where template_id = $2`, [id, i.copyFrom]);
  await log(adminId, "template.create", id, i); return { id };
}
