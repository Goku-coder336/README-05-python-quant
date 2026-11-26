import { one, pool, q } from "./db";

// Event planner data. Every function that reads or changes an event takes the
// signed-in user's id and only touches events that user owns.

export type EventType = { id: string; slug: string; name: string; icon: string; grp: string };
export type EventRow = {
  id: string; title: string; eventTypeId: string; eventType: string; traditionId: string | null; tradition: string | null;
  cityId: string; city: string; citySlug: string; countryCode: string; guestCount: number | null; sizeTier: "intimate" | "standard";
  budgetMinor: number | null; currency: string; eventDate: string | null;
};
export type ItemStatus = "todo" | "shortlisted" | "booked" | "skipped";
export type EventItem = {
  id: string; categoryId: string; categorySlug: string; categoryName: string; categoryIcon: string; categoryKind: "service" | "equipment";
  subEvent: string; label: string; note: string; budgetShare: number; status: ItemStatus; sort: number;
};
export type ShortlistEntry = { eventItemId: string; itemKind: "service" | "equipment"; itemId: string; title: string; vendor: string; priceMinor: number; currency: string };
export type EventBooking = { id: string; eventItemId: string | null; itemTitle: string; status: string; subtotalMinor: number; currency: string; startsOn: string };

const GROUP_ORDER = `array_position(array['Weddings and family','Religious and cultural','Parties and celebrations','Business and professional','Community and public','Something else'], grp)`;
export const eventTypes = () => q<EventType>(`select id, slug, name, icon, grp from event_types where active order by ${GROUP_ORDER} nulls last, sort, name`);

const EVENT = `e.id, e.title, e.event_type_id as "eventTypeId", et.name as "eventType", e.tradition_id as "traditionId", t.name as tradition,
  e.city_id as "cityId", r.name as city, r.slug as "citySlug", lower(r.country_code) as "countryCode", e.guest_count as "guestCount",
  e.size_tier as "sizeTier", e.budget_minor as "budgetMinor", e.currency, e.event_date as "eventDate"`;
const EVENT_FROM = `from events e join event_types et on et.id = e.event_type_id join regions r on r.id = e.city_id left join traditions t on t.id = e.tradition_id`;

export const myEvents = (userId: string) => q<EventRow>(`select ${EVENT} ${EVENT_FROM} where e.owner_id = $1 order by e.event_date nulls last, e.created_at desc`, [userId]);
export const myEvent = (id: string, userId: string) => one<EventRow>(`select ${EVENT} ${EVENT_FROM} where e.id = $1 and e.owner_id = $2`, [id, userId]);

/** Picks the closest template: exact tradition first, then any tradition; intimate size first when the event is small. */
async function pickTemplate(eventTypeId: string, traditionId: string | null, sizeTier: "intimate" | "standard") {
  return one<{ id: string }>(`select id from event_templates where event_type_id = $1
    order by (tradition_id is not distinct from $2) desc, (size_tier = $3) desc, (tradition_id is null) desc limit 1`, [eventTypeId, traditionId, sizeTier]);
}

export async function createEvent(userId: string, i: { eventTypeId: string; traditionId: string | null; cityId: string; title: string; guestCount: number | null; budgetMinor: number | null; eventDate: string | null }) {
  const sizeTier = i.guestCount !== null && i.guestCount <= 50 ? "intimate" : "standard";
  const cur = await one<{ currency: string }>(`select c.currency from regions r join countries c on c.code = r.country_code where r.id = $1`, [i.cityId]);
  if (!cur) return null;
  // Intimate events use the intimate template when one exists for the occasion, whatever the tradition.
  const tpl = (sizeTier === "intimate" && await one<{ id: string }>(`select id from event_templates where event_type_id = $1 and size_tier = 'intimate' and tradition_id is null`, [i.eventTypeId]))
    || await pickTemplate(i.eventTypeId, i.traditionId, sizeTier);
  const c = await pool.connect();
  try {
    await c.query("begin");
    const ev = (await c.query(`insert into events (owner_id,event_type_id,tradition_id,city_id,title,guest_count,size_tier,budget_minor,currency,event_date)
      values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) returning id`, [userId, i.eventTypeId, i.traditionId, i.cityId, i.title, i.guestCount, sizeTier, i.budgetMinor, cur.currency, i.eventDate])).rows[0] as { id: string };
    if (tpl) await c.query(`insert into event_items (event_id, category_id, sub_event, label, note, budget_share, sort)
      select $1, category_id, sub_event, label, note, budget_share, sort from event_template_items where template_id = $2`, [ev.id, tpl.id]);
    await c.query("commit");
    return ev;
  } catch (e) { await c.query("rollback"); throw e; } finally { c.release(); }
}

export async function eventItems(eventId: string, userId: string) {
  return q<EventItem>(`select i.id, i.category_id as "categoryId", k.slug as "categorySlug", k.name as "categoryName", k.icon as "categoryIcon", k.kind as "categoryKind",
      i.sub_event as "subEvent", i.label, i.note, i.budget_share as "budgetShare", i.status, i.sort
    from event_items i join events e on e.id = i.event_id join categories k on k.id = i.category_id
    where i.event_id = $1 and e.owner_id = $2 order by i.sort, i.label`, [eventId, userId]);
}

export async function shortlistFor(eventId: string, userId: string) {
  return q<ShortlistEntry>(`select s.event_item_id as "eventItemId", s.item_kind as "itemKind", s.item_id as "itemId",
      coalesce(sv.title, eq.title) as title, v.business_name as vendor,
      coalesce(sv.price_minor, eq.day_rate_minor) as "priceMinor", coalesce(sv.currency, eq.currency) as currency
    from shortlist s join event_items i on i.id = s.event_item_id join events e on e.id = i.event_id
    left join services sv on s.item_kind = 'service' and sv.id = s.item_id
    left join equipment eq on s.item_kind = 'equipment' and eq.id = s.item_id
    join vendors v on v.id = coalesce(sv.vendor_id, eq.vendor_id)
    where e.id = $1 and e.owner_id = $2 order by s.created_at`, [eventId, userId]);
}

export async function eventBookings(eventId: string, userId: string) {
  return q<EventBooking>(`select b.id, b.event_item_id as "eventItemId", b.item_title as "itemTitle", b.status, b.subtotal_minor as "subtotalMinor", b.currency, b.starts_on as "startsOn"
    from bookings b join event_items i on i.id = b.event_item_id join events e on e.id = i.event_id
    where e.id = $1 and e.owner_id = $2 and b.status in ('requested','accepted','completed') order by b.starts_on`, [eventId, userId]);
}

export async function setItemStatus(itemId: string, userId: string, status: ItemStatus) {
  const r = await pool.query(`update event_items i set status = $3 from events e where i.id = $1 and e.id = i.event_id and e.owner_id = $2`, [itemId, userId, status]);
  return (r.rowCount ?? 0) > 0;
}

export async function addItem(eventId: string, userId: string, i: { categoryId: string; label: string; subEvent: string }) {
  return one(`insert into event_items (event_id, category_id, sub_event, label, sort)
    select e.id, $3, $5, $4, coalesce((select max(sort) + 1 from event_items where event_id = e.id), 1) from events e where e.id = $1 and e.owner_id = $2 returning id`,
    [eventId, userId, i.categoryId, i.label, i.subEvent]);
}

export async function removeItem(itemId: string, userId: string) {
  await pool.query(`delete from event_items i using events e where i.id = $1 and e.id = i.event_id and e.owner_id = $2
    and not exists (select 1 from bookings b where b.event_item_id = i.id and b.status in ('requested','accepted'))`, [itemId, userId]);
}

/** Saves a listing to the matching checklist item. Creates the item if the event has none for that category. */
export async function saveToEvent(eventId: string, userId: string, itemKind: "service" | "equipment", itemId: string) {
  const ev = await one<{ id: string }>(`select id from events where id = $1 and owner_id = $2`, [eventId, userId]);
  if (!ev) return null;
  const listing = await one<{ categoryId: string; title: string }>(itemKind === "service"
    ? `select category_id as "categoryId", title from services where id = $1` : `select category_id as "categoryId", title from equipment where id = $1`, [itemId]);
  if (!listing) return null;
  let item = await one<{ id: string }>(`select id from event_items where event_id = $1 and category_id = $2 and status <> 'skipped' order by (status = 'booked'), sort limit 1`, [eventId, listing.categoryId]);
  if (!item) {
    const cat = (await one<{ name: string }>(`select name from categories where id = $1`, [listing.categoryId]))!;
    item = (await addItem(eventId, userId, { categoryId: listing.categoryId, label: cat.name, subEvent: "Added by you" })) as { id: string };
  }
  await pool.query(`insert into shortlist (event_item_id, item_kind, item_id) values ($1,$2,$3) on conflict do nothing`, [item.id, itemKind, itemId]);
  await pool.query(`update event_items set status = 'shortlisted' where id = $1 and status = 'todo'`, [item.id]);
  return item;
}

export async function unsave(eventItemId: string, userId: string, itemKind: "service" | "equipment", itemId: string) {
  await pool.query(`delete from shortlist s using event_items i, events e where s.event_item_id = $1 and s.item_kind = $3 and s.item_id = $4
    and i.id = s.event_item_id and e.id = i.event_id and e.owner_id = $2`, [eventItemId, userId, itemKind, itemId]);
  await pool.query(`update event_items i set status = 'todo' from events e where i.id = $1 and e.id = i.event_id and e.owner_id = $2
    and i.status = 'shortlisted' and not exists (select 1 from shortlist where event_item_id = i.id)`, [eventItemId, userId]);
}

/** The event item a booking should tick off, only if the signed-in user owns it. */
export async function ownedItemForBooking(eventItemId: string, userId: string) {
  return one<{ id: string }>(`select i.id from event_items i join events e on e.id = i.event_id where i.id = $1 and e.owner_id = $2`, [eventItemId, userId]);
}

export async function deleteEvent(eventId: string, userId: string) {
  await pool.query(`update bookings set event_item_id = null where event_item_id in (select i.id from event_items i join events e on e.id = i.event_id where e.id = $1 and e.owner_id = $2)`, [eventId, userId]);
  await pool.query(`delete from events where id = $1 and owner_id = $2`, [eventId, userId]);
}

/** Label and event for a checklist item, only if the user owns it. Used for "Booking for …" banners. */
export async function itemContext(eventItemId: string, userId: string) {
  return one<{ itemId: string; label: string; eventId: string; eventTitle: string; eventDate: string | null }>(
    `select i.id as "itemId", i.label, e.id as "eventId", e.title as "eventTitle", e.event_date as "eventDate"
     from event_items i join events e on e.id = i.event_id where i.id = $1 and e.owner_id = $2`, [eventItemId, userId]);
}
