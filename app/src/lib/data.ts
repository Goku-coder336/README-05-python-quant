import type { PoolClient } from "pg";
import { one, pool, q } from "./db";
import type { Booking, Category, Country, Equipment, Region, Service, Tradition, Vendor } from "./types";

// Postgres data layer. Same functions as the earlier JSON version, now async.
// Authorisation: every vendor write takes the signed-in user id and checks ownership in SQL.

const COUNTRY = `code, name, currency, locale, tax_name as "taxName", tax_rate_bp as "taxRateBp", active`;
const REGION = `id, country_code as "countryCode", parent_id as "parentId", kind, name, slug, timezone, active`;
const VENDOR = `v.id, v.owner_id as "ownerId", v.handle, v.business_name as "businessName", v.bio, v.base_region_id as "baseRegionId",
  v.serves_region_ids as "servesRegionIds", v.phone, v.verification, v.rating_avg as "ratingAvg", v.rating_count as "ratingCount",
  v.tradition_ids as "traditionIds", v.created_at as "createdAt"`;
const SERVICE = `s.id, s.vendor_id as "vendorId", s.category_id as "categoryId", s.title, s.description, s.included, s.price_minor as "priceMinor",
  s.currency, s.price_unit as "priceUnit", s.min_guests as "minGuests", s.max_guests as "maxGuests", s.advance_pct as "advancePct",
  s.styles, s.tradition_ids as "traditionIds", s.status`;
const EQUIP = `e.id, e.vendor_id as "vendorId", e.category_id as "categoryId", e.title, e.description, e.specs, e.day_rate_minor as "dayRateMinor",
  e.deposit_minor as "depositMinor", e.currency, e.needs_operator as "needsOperator", e.units, e.status`;
const BOOKING = `id, vendor_id as "vendorId", item_kind as "itemKind", item_id as "itemId", item_title as "itemTitle", customer_name as "customerName",
  customer_phone as "customerPhone", note, starts_on as "startsOn", ends_on as "endsOn", unit_index as "unitIndex", subtotal_minor as "subtotalMinor",
  tax_minor as "taxMinor", deposit_minor as "depositMinor", currency, status, created_at as "createdAt"`;

export type VendorRow = Vendor & { ownerId: string | null };

// ---------- places ----------
export const countries = () => q<Country>(`select ${COUNTRY} from countries order by active desc, name`);
export const country = (code: string) => one<Country>(`select ${COUNTRY} from countries where code = upper($1)`, [code]);
export const cities = (countryCode?: string) =>
  q<Region>(`select ${REGION} from regions where kind='city' and ($1::text is null or country_code = upper($1)) order by name`, [countryCode ?? null]);
export const city = (countryCode: string, slug: string) =>
  one<Region>(`select ${REGION} from regions where kind='city' and country_code = upper($1) and slug = $2`, [countryCode, slug]);
export const region = (id: string) => one<Region>(`select ${REGION} from regions where id = $1`, [id]);
export const traditions = () => q<Tradition>(`select id, slug, name from traditions order by name`);
export const categories = () => q<Category>(`select id, slug, name, kind, icon from categories order by kind desc, name`);
export const category = (slug: string) => one<Category>(`select id, slug, name, kind, icon from categories where slug = $1`, [slug]);

// ---------- discovery ----------
export type Listing =
  | { kind: "service"; item: Service; vendor: Vendor }
  | { kind: "equipment"; item: Equipment; vendor: Vendor };

export async function listings(o: { cityId: string; categoryId?: string; intimate?: boolean; traditionId?: string }): Promise<Listing[]> {
  const vendors = await q<VendorRow>(`select ${VENDOR} from vendors v where $1 = any(v.serves_region_ids)`, [o.cityId]);
  const byId = new Map(vendors.map(v => [v.id, v]));
  const ids = vendors.map(v => v.id);
  if (!ids.length) return [];
  const services = await q<Service>(
    `select ${SERVICE} from services s where s.vendor_id = any($1) and s.status='live'
       and ($2::text is null or s.category_id = $2)
       and (not $3 or (s.max_guests is not null and s.max_guests <= 50) or 'intimate' = any(s.styles))
       and ($4::text is null or $4 = any(s.tradition_ids) or 't-any' = any(s.tradition_ids))`,
    [ids, o.categoryId ?? null, !!o.intimate, o.traditionId ?? null]);
  const equipment = o.traditionId ? [] : await q<Equipment>(
    `select ${EQUIP} from equipment e where e.vendor_id = any($1) and e.status='live' and ($2::text is null or e.category_id = $2)`, [ids, o.categoryId ?? null]);
  const out: Listing[] = [
    ...services.map(item => ({ kind: "service" as const, item, vendor: byId.get(item.vendorId)! })),
    ...equipment.map(item => ({ kind: "equipment" as const, item, vendor: byId.get(item.vendorId)! })),
  ];
  return out.sort((a, b) => Number(b.vendor.verification === "verified") - Number(a.vendor.verification === "verified") || b.vendor.ratingAvg - a.vendor.ratingAvg);
}

export const vendorByHandle = (handle: string) => one<VendorRow>(`select ${VENDOR} from vendors v where handle = $1`, [handle]);
export const vendorById = (id: string) => one<VendorRow>(`select ${VENDOR} from vendors v where id = $1`, [id]);
export const vendorsOwnedBy = (userId: string) => q<VendorRow>(`select ${VENDOR} from vendors v where owner_id = $1 order by created_at`, [userId]);
export const service = (id: string) => one<Service>(`select ${SERVICE} from services s where id = $1`, [id]);
export const equipmentItem = (id: string) => one<Equipment>(`select ${EQUIP} from equipment e where id = $1`, [id]);
export async function vendorItems(vendorId: string) {
  const [services, equipment] = await Promise.all([
    q<Service>(`select ${SERVICE} from services s where vendor_id = $1 order by created_at desc`, [vendorId]),
    q<Equipment>(`select ${EQUIP} from equipment e where vendor_id = $1 order by created_at desc`, [vendorId]),
  ]);
  return { services, equipment };
}

// ---------- bookings ----------
export const booking = (id: string) => one<Booking & { customerId: string | null }>(`select ${BOOKING}, customer_id as "customerId" from bookings where id = $1`, [id]);

/** Only the vendor's owner may list its bookings. Returns null when not allowed. */
export async function vendorBookings(vendorId: string, userId: string) {
  const v = await one(`select 1 from vendors where id = $1 and owner_id = $2`, [vendorId, userId]);
  if (!v) return null;
  return q<Booking>(`select ${BOOKING} from bookings where vendor_id = $1 order by created_at desc`, [vendorId]);
}

const days = (a: string, b: string) => Math.round((Date.parse(b) - Date.parse(a)) / 86400000) + 1;
const isExclusion = (e: unknown) => (e as { code?: string }).code === "23P01";

async function tx<T>(fn: (c: PoolClient) => Promise<T>) {
  const c = await pool.connect();
  try { await c.query("begin"); const r = await fn(c); await c.query("commit"); return r; }
  catch (e) { await c.query("rollback"); throw e; }
  finally { c.release(); }
}

export async function createBooking(input: { itemKind: "service" | "equipment"; itemId: string; startsOn: string; endsOn: string; customerName: string; customerPhone: string; note: string; customerId: string | null; eventItemId?: string | null }):
  Promise<{ ok: true; booking: Booking } | { ok: false; error: string }> {
  if (input.endsOn < input.startsOn) return { ok: false, error: "The end date is before the start date." };
  if (days(input.startsOn, input.endsOn) > 30) return { ok: false, error: "Rentals can be booked for up to 30 days at a time." };

  if (input.itemKind === "equipment") {
    const e = await equipmentItem(input.itemId);
    if (!e || e.status !== "live") return { ok: false, error: "This item is no longer listed." };
    const c = (await one<Country>(`select ${COUNTRY} from countries where currency = $1 limit 1`, [e.currency]))!;
    const sub = e.dayRateMinor * days(input.startsOn, input.endsOn);
    // Try each physical unit; the exclusion constraint rejects any unit already held for those days.
    for (let unit = 0; unit < e.units; unit++) {
      try {
        const b = await tx(async cl => {
          const [row] = (await cl.query(`insert into bookings (vendor_id,customer_id,item_kind,item_id,item_title,customer_name,customer_phone,note,starts_on,ends_on,unit_index,subtotal_minor,tax_minor,deposit_minor,currency,event_item_id)
            values ($1,$2,'equipment',$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15) returning ${BOOKING}`,
            [e.vendorId, input.customerId, e.id, e.title, input.customerName, input.customerPhone, input.note, input.startsOn, input.endsOn, unit, sub, Math.round(sub * c.taxRateBp / 10000), e.depositMinor, e.currency, input.eventItemId ?? null])).rows;
          if (input.eventItemId) await cl.query(`update event_items set status = 'booked' where id = $1`, [input.eventItemId]);
          await cl.query(`insert into unit_holds values ($1,$2,$3,daterange($4::date,$5::date,'[]'))`, [row.id, e.id, unit, input.startsOn, input.endsOn]);
          return row as Booking;
        });
        return { ok: true, booking: b };
      } catch (err) { if (!isExclusion(err)) throw err; }
    }
    return { ok: false, error: "All units are booked for those dates. Try other dates." };
  }

  const s = await service(input.itemId);
  if (!s || s.status !== "live") return { ok: false, error: "This package is no longer listed." };
  const c = (await one<Country>(`select ${COUNTRY} from countries where currency = $1 limit 1`, [s.currency]))!;
  try {
    const b = await tx(async cl => {
      const [row] = (await cl.query(`insert into bookings (vendor_id,customer_id,item_kind,item_id,item_title,customer_name,customer_phone,note,starts_on,ends_on,subtotal_minor,tax_minor,currency,event_item_id)
        values ($1,$2,'service',$3,$4,$5,$6,$7,$8,$8,$9,$10,$11,$12) returning ${BOOKING}`,
        [s.vendorId, input.customerId, s.id, s.title, input.customerName, input.customerPhone, input.note, input.startsOn, s.priceMinor, Math.round(s.priceMinor * c.taxRateBp / 10000), s.currency, input.eventItemId ?? null])).rows;
      if (input.eventItemId) await cl.query(`update event_items set status = 'booked' where id = $1`, [input.eventItemId]);
      await cl.query(`insert into vendor_day_holds values ($1,$2,daterange($3::date,$3::date,'[]'))`, [row.id, s.vendorId, input.startsOn]);
      return row as Booking;
    });
    return { ok: true, booking: b };
  } catch (err) {
    if (isExclusion(err)) return { ok: false, error: "This vendor is already booked that day. Try another date." };
    throw err;
  }
}

/** Owner-only. Declining releases the held unit or day. */
export async function setBookingStatus(bookingId: string, userId: string, status: "accepted" | "declined") {
  return tx(async cl => {
    const r = await cl.query(`update bookings b set status = $3 from vendors v
      where b.id = $1 and b.vendor_id = v.id and v.owner_id = $2 and b.status = 'requested' returning b.id`, [bookingId, userId, status]);
    if (!r.rowCount) return false;
    if (status === "declined") {
      await cl.query(`delete from unit_holds where booking_id = $1`, [bookingId]);
      await cl.query(`delete from vendor_day_holds where booking_id = $1`, [bookingId]);
      // Put the customer's checklist item back to shortlisted (or to do) unless another booking still covers it.
      await cl.query(`update event_items i set status = case when exists (select 1 from shortlist s where s.event_item_id = i.id) then 'shortlisted' else 'todo' end
        from bookings b where b.id = $1 and i.id = b.event_item_id and i.status = 'booked'
        and not exists (select 1 from bookings o where o.event_item_id = i.id and o.id <> b.id and o.status in ('requested','accepted'))`, [bookingId]);
    }
    return true;
  });
}

// ---------- vendor side ----------
export async function createVendor(ownerId: string, input: { businessName: string; phone: string; cityId: string; bio: string; traditionIds: string[] }) {
  const base = input.businessName.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 40) || "vendor";
  for (let n = 1; n < 50; n++) {
    const handle = n === 1 ? base : `${base}-${n}`;
    const row = await one<VendorRow>(`insert into vendors (owner_id,handle,business_name,bio,base_region_id,serves_region_ids,phone,tradition_ids)
      values ($1,$2,$3,$4,$5,array[$5],$6,$7) on conflict (handle) do nothing returning id, handle`,
      [ownerId, handle, input.businessName, input.bio, input.cityId, input.phone, input.traditionIds]);
    if (row) return row;
  }
  throw new Error("Could not create a unique handle");
}

async function ownedVendorCurrency(vendorId: string, userId: string) {
  return one<{ currency: string }>(`select c.currency from vendors v join regions r on r.id = v.base_region_id join countries c on c.code = r.country_code
    where v.id = $1 and v.owner_id = $2`, [vendorId, userId]);
}

export async function addService(vendorId: string, userId: string, i: Omit<Service, "id" | "vendorId" | "status" | "currency">) {
  const own = await ownedVendorCurrency(vendorId, userId); if (!own) return null;
  return one(`insert into services (vendor_id,category_id,title,description,included,price_minor,currency,price_unit,min_guests,max_guests,advance_pct,styles,tradition_ids)
    values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13) returning id`,
    [vendorId, i.categoryId, i.title, i.description, i.included, i.priceMinor, own.currency, i.priceUnit, i.minGuests, i.maxGuests, i.advancePct, i.styles, i.traditionIds]);
}

export async function addEquipment(vendorId: string, userId: string, i: Omit<Equipment, "id" | "vendorId" | "status" | "currency">) {
  const own = await ownedVendorCurrency(vendorId, userId); if (!own) return null;
  return one(`insert into equipment (vendor_id,category_id,title,description,specs,day_rate_minor,deposit_minor,currency,needs_operator,units)
    values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) returning id`,
    [vendorId, i.categoryId, i.title, i.description, i.specs, i.dayRateMinor, i.depositMinor, own.currency, i.needsOperator, i.units]);
}

// ---------- waitlist ----------
export async function joinWaitlist(email: string, role: "customer" | "vendor", city: string) {
  await q(`insert into waitlist (email, role, city) values ($1,$2,$3) on conflict (email, role) do update set city = excluded.city`, [email, role, city]);
}
