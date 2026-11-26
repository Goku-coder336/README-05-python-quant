"use server";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import * as data from "@/lib/data";

export type FormState = { error?: string; fields?: Record<string, string> };

const str = (f: FormData, k: string) => String(f.get(k) ?? "").trim();
const isDate = (s: string) => /^\d{4}-\d{2}-\d{2}$/.test(s);
const today = () => new Date().toISOString().slice(0, 10);

export async function requestBooking(_: FormState, f: FormData): Promise<FormState> {
  const fields = Object.fromEntries([...f.entries()].map(([k, v]) => [k, String(v)]));
  const kind = str(f, "kind") as "service" | "equipment";
  const startsOn = str(f, "startsOn"), endsOn = str(f, "endsOn") || startsOn;
  const name = str(f, "name"), phone = str(f, "phone");
  if (!isDate(startsOn)) return { error: "Choose a date.", fields };
  if (startsOn < today()) return { error: "That date has passed. Choose a future date.", fields };
  if (name.length < 2) return { error: "Enter your name.", fields };
  if (!/^\+?[0-9 ]{8,16}$/.test(phone)) return { error: "Enter a phone number with country code, for example +91 98470 12345.", fields };
  const r = data.createBooking({ itemKind: kind, itemId: str(f, "itemId"), startsOn, endsOn, customerName: name, customerPhone: phone.replace(/\s/g, ""), note: str(f, "note").slice(0, 500) });
  if (!r.ok) return { error: r.error, fields };
  redirect(`/bookings/${r.booking.id}`);
}

export async function joinAsVendor(_: FormState, f: FormData): Promise<FormState> {
  const fields = Object.fromEntries([...f.entries()].map(([k, v]) => [k, String(v)]));
  const businessName = str(f, "businessName"), phone = str(f, "phone"), cityId = str(f, "cityId");
  if (businessName.length < 2) return { error: "Enter your business name.", fields };
  if (!/^\+?[0-9 ]{8,16}$/.test(phone)) return { error: "Enter a WhatsApp number with country code.", fields };
  if (!data.region(cityId)) return { error: "Choose your city.", fields };
  const v = data.createVendor({ businessName, phone: phone.replace(/\s/g, ""), cityId, bio: str(f, "bio").slice(0, 400), traditionIds: f.getAll("traditionIds").map(String) });
  redirect(`/vendor/${v.handle}?welcome=1`);
}

export async function addListing(_: FormState, f: FormData): Promise<FormState> {
  const fields = Object.fromEntries([...f.entries()].map(([k, v]) => [k, String(v)]));
  const vendor = data.vendorByHandle(str(f, "handle"));
  if (!vendor) return { error: "Vendor not found." };
  const cat = data.categories().find(c => c.id === str(f, "categoryId"));
  if (!cat) return { error: "Choose a category.", fields };
  const title = str(f, "title"); const price = Number(str(f, "price"));
  if (title.length < 3) return { error: "Give the listing a title.", fields };
  if (!Number.isFinite(price) || price <= 0) return { error: "Enter a price above zero.", fields };
  if (cat.kind === "service") {
    const max = Number(str(f, "maxGuests"));
    data.addService(vendor.id, { categoryId: cat.id, title, description: str(f, "description"), included: str(f, "included").split(",").map(s => s.trim()).filter(Boolean), priceMinor: Math.round(price * 100), priceUnit: "event", minGuests: null, maxGuests: max > 0 ? max : null, advancePct: 30, styles: max > 0 && max <= 50 ? ["intimate"] : [], traditionIds: vendor.traditionIds });
  } else {
    const deposit = Number(str(f, "deposit")) || 0; const units = Math.max(1, Math.min(50, Number(str(f, "units")) || 1));
    data.addEquipment(vendor.id, { categoryId: cat.id, title, description: str(f, "description"), specs: {}, dayRateMinor: Math.round(price * 100), depositMinor: Math.round(deposit * 100), needsOperator: f.get("needsOperator") === "on", units });
  }
  revalidatePath(`/vendor/${vendor.handle}`);
  return { fields: {} };
}

export async function decideBooking(f: FormData) {
  const vendor = data.vendorByHandle(str(f, "handle"));
  if (!vendor) return;
  const d = str(f, "decision");
  if (d === "accepted" || d === "declined") data.setBookingStatus(str(f, "bookingId"), vendor.id, d);
  revalidatePath(`/vendor/${vendor.handle}`);
}
