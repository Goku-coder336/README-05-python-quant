import fs from "node:fs";
import path from "node:path";
import { seed } from "./seed";
import type { Booking, DB, Equipment, Region, Service, Vendor } from "./types";

// Fake data layer: a JSON file in .data/. replica-backend swaps this for Postgres
// with the same function signatures, so no screen code changes.
const FILE = path.join(process.cwd(), ".data", "db.json");

function load(): DB {
  try { return JSON.parse(fs.readFileSync(FILE, "utf8")) as DB; }
  catch { save(seed); return structuredClone(seed); }
}
function save(db: DB) {
  fs.mkdirSync(path.dirname(FILE), { recursive: true });
  fs.writeFileSync(FILE, JSON.stringify(db, null, 2));
}
const id = (p: string) => `${p}-${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;

// ---------- places ----------
export function countries() { return load().countries; }
export function country(code: string) { return load().countries.find(c => c.code.toLowerCase() === code.toLowerCase()) ?? null; }
export function cities(countryCode?: string) {
  return load().regions.filter(r => r.kind === "city" && (!countryCode || r.countryCode === countryCode.toUpperCase()));
}
export function city(countryCode: string, slug: string): Region | null {
  return load().regions.find(r => r.kind === "city" && r.countryCode === countryCode.toUpperCase() && r.slug === slug) ?? null;
}
export function region(id: string) { return load().regions.find(r => r.id === id) ?? null; }
export function traditions() { return load().traditions; }
export function categories() { return load().categories; }
export function category(slug: string) { return load().categories.find(c => c.slug === slug) ?? null; }

// ---------- discovery ----------
export type Listing =
  | { kind: "service"; item: Service; vendor: Vendor }
  | { kind: "equipment"; item: Equipment; vendor: Vendor };

export function listings(opts: { cityId: string; categoryId?: string; intimate?: boolean; traditionId?: string }): Listing[] {
  const db = load();
  const vendorsHere = new Map(db.vendors.filter(v => v.servesRegionIds.includes(opts.cityId)).map(v => [v.id, v]));
  const out: Listing[] = [];
  for (const s of db.services) {
    const v = vendorsHere.get(s.vendorId);
    if (!v || s.status !== "live") continue;
    if (opts.categoryId && s.categoryId !== opts.categoryId) continue;
    if (opts.intimate && !(s.maxGuests !== null && s.maxGuests <= 50) && !s.styles.includes("intimate")) continue;
    if (opts.traditionId && !s.traditionIds.includes(opts.traditionId) && !s.traditionIds.includes("t-any")) continue;
    out.push({ kind: "service", item: s, vendor: v });
  }
  if (!opts.traditionId) {
    for (const e of db.equipment) {
      const v = vendorsHere.get(e.vendorId);
      if (!v || e.status !== "live") continue;
      if (opts.categoryId && e.categoryId !== opts.categoryId) continue;
      out.push({ kind: "equipment", item: e, vendor: v });
    }
  }
  return out.sort((a, b) => Number(b.vendor.verification === "verified") - Number(a.vendor.verification === "verified") || b.vendor.ratingAvg - a.vendor.ratingAvg);
}

export function vendorByHandle(handle: string) { return load().vendors.find(v => v.handle === handle) ?? null; }
export function vendorById(id: string) { return load().vendors.find(v => v.id === id) ?? null; }
export function service(id: string) { return load().services.find(s => s.id === id) ?? null; }
export function equipmentItem(id: string) { return load().equipment.find(e => e.id === id) ?? null; }
export function vendorItems(vendorId: string) {
  const db = load();
  return { services: db.services.filter(s => s.vendorId === vendorId), equipment: db.equipment.filter(e => e.vendorId === vendorId) };
}

// ---------- availability ----------
const overlaps = (a1: string, a2: string, b1: string, b2: string) => a1 <= b2 && b1 <= a2;
const holding = (b: Booking) => b.status === "requested" || b.status === "accepted";

/** Index of a free physical unit for the date range, or null when all are held. */
export function freeUnit(equipmentId: string, startsOn: string, endsOn: string): number | null {
  const db = load();
  const e = db.equipment.find(x => x.id === equipmentId);
  if (!e) return null;
  const taken = new Set(db.bookings.filter(b => b.itemKind === "equipment" && b.itemId === equipmentId && holding(b) && overlaps(b.startsOn, b.endsOn, startsOn, endsOn)).map(b => b.unitIndex));
  for (let i = 0; i < e.units; i++) if (!taken.has(i)) return i;
  return null;
}
export function vendorBusyOn(vendorId: string, date: string) {
  return load().bookings.some(b => b.vendorId === vendorId && b.itemKind === "service" && holding(b) && overlaps(b.startsOn, b.endsOn, date, date));
}

// ---------- bookings ----------
export function booking(id: string) { return load().bookings.find(b => b.id === id) ?? null; }
export function vendorBookings(vendorId: string) {
  return load().bookings.filter(b => b.vendorId === vendorId).sort((a, b) => b.createdAt.localeCompare(a.createdAt));
}

const days = (a: string, b: string) => Math.round((Date.parse(b) - Date.parse(a)) / 86400000) + 1;

export function createBooking(input: { itemKind: "service" | "equipment"; itemId: string; startsOn: string; endsOn: string; customerName: string; customerPhone: string; note: string }):
  { ok: true; booking: Booking } | { ok: false; error: string } {
  const db = load();
  if (input.endsOn < input.startsOn) return { ok: false, error: "The end date is before the start date." };
  let b: Booking;
  if (input.itemKind === "equipment") {
    const e = db.equipment.find(x => x.id === input.itemId);
    if (!e) return { ok: false, error: "This item is no longer listed." };
    const unit = freeUnit(e.id, input.startsOn, input.endsOn);
    if (unit === null) return { ok: false, error: "All units are booked for those dates. Try other dates." };
    const sub = e.dayRateMinor * days(input.startsOn, input.endsOn);
    const c = db.countries.find(c => c.currency === e.currency)!;
    b = { id: id("b"), vendorId: e.vendorId, itemKind: "equipment", itemId: e.id, itemTitle: e.title, customerName: input.customerName, customerPhone: input.customerPhone, note: input.note, startsOn: input.startsOn, endsOn: input.endsOn, unitIndex: unit, subtotalMinor: sub, taxMinor: Math.round(sub * c.taxRateBp / 10000), depositMinor: e.depositMinor, currency: e.currency, status: "requested", createdAt: new Date().toISOString() };
  } else {
    const s = db.services.find(x => x.id === input.itemId);
    if (!s) return { ok: false, error: "This package is no longer listed." };
    if (vendorBusyOn(s.vendorId, input.startsOn)) return { ok: false, error: "This vendor is already booked that day. Try another date." };
    const c = db.countries.find(c => c.currency === s.currency)!;
    b = { id: id("b"), vendorId: s.vendorId, itemKind: "service", itemId: s.id, itemTitle: s.title, customerName: input.customerName, customerPhone: input.customerPhone, note: input.note, startsOn: input.startsOn, endsOn: input.startsOn, unitIndex: null, subtotalMinor: s.priceMinor, taxMinor: Math.round(s.priceMinor * c.taxRateBp / 10000), depositMinor: 0, currency: s.currency, status: "requested", createdAt: new Date().toISOString() };
  }
  db.bookings.push(b); save(db);
  return { ok: true, booking: b };
}

export function setBookingStatus(bookingId: string, vendorId: string, status: "accepted" | "declined") {
  const db = load();
  const b = db.bookings.find(x => x.id === bookingId && x.vendorId === vendorId);
  if (!b || b.status !== "requested") return false;
  b.status = status; save(db); return true;
}

// ---------- vendor side ----------
export function createVendor(input: { businessName: string; phone: string; cityId: string; bio: string; traditionIds: string[] }): Vendor {
  const db = load();
  const base = input.businessName.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 40) || "vendor";
  let handle = base, n = 2;
  while (db.vendors.some(v => v.handle === handle)) handle = `${base}-${n++}`;
  const v: Vendor = { id: id("v"), handle, businessName: input.businessName, bio: input.bio, baseRegionId: input.cityId, servesRegionIds: [input.cityId], phone: input.phone, verification: "pending", ratingAvg: 0, ratingCount: 0, traditionIds: input.traditionIds, createdAt: new Date().toISOString() };
  db.vendors.push(v); save(db); return v;
}

export function addService(vendorId: string, input: Omit<Service, "id" | "vendorId" | "status" | "currency">) {
  const db = load();
  const v = db.vendors.find(x => x.id === vendorId)!;
  const cur = db.countries.find(c => c.code === db.regions.find(r => r.id === v.baseRegionId)!.countryCode)!.currency;
  const s: Service = { ...input, id: id("s"), vendorId, currency: cur, status: "live" };
  db.services.push(s); save(db); return s;
}

export function addEquipment(vendorId: string, input: Omit<Equipment, "id" | "vendorId" | "status" | "currency">) {
  const db = load();
  const v = db.vendors.find(x => x.id === vendorId)!;
  const cur = db.countries.find(c => c.code === db.regions.find(r => r.id === v.baseRegionId)!.countryCode)!.currency;
  const e: Equipment = { ...input, id: id("e"), vendorId, currency: cur, status: "live" };
  db.equipment.push(e); save(db); return e;
}
