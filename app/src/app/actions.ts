"use server";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { z } from "zod";
import * as data from "@/lib/data";
import { currentUser, deleteAccount, requestCode, signOut, verifyCode } from "@/lib/auth";
import { limited } from "@/lib/ratelimit";

export type FormState = { error?: string; fields?: Record<string, string>; step?: "code"; ok?: boolean };

const fieldsOf = (f: FormData) => Object.fromEntries([...f.entries()].filter(([k]) => !k.startsWith("$")).map(([k, v]) => [k, String(v)]));
const date = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Choose a date.");
const phone = z.string().trim().regex(/^\+?[0-9 ]{8,16}$/, "Enter a phone number with country code, for example +91 98470 12345.").transform(s => s.replace(/\s/g, ""));
const safeNext = (n: string) => (n.startsWith("/") && !n.startsWith("//") ? n : "/account");
const first = (e: z.ZodError) => e.issues[0]?.message ?? "Check the form and try again.";

// ---------- sign in ----------
export async function sendCode(_: FormState, f: FormData): Promise<FormState> {
  const fields = fieldsOf(f);
  if (await limited("code", 10, 3600_000)) return { error: "Too many attempts from this connection. Try again later.", fields };
  const r = await requestCode(String(f.get("email") ?? ""));
  return r.ok ? { step: "code", fields } : { error: r.error, fields };
}

export async function checkCode(_: FormState, f: FormData): Promise<FormState> {
  const fields = fieldsOf(f);
  if (await limited("verify", 30, 3600_000)) return { error: "Too many attempts. Try again later.", fields, step: "code" };
  const r = await verifyCode(String(f.get("email") ?? ""), String(f.get("code") ?? ""));
  if (!r.ok) return { error: r.error, fields, step: "code" };
  redirect(safeNext(String(f.get("next") ?? "/account")));
}

export async function signOutAction(f: FormData) { await signOut(f.get("everywhere") === "1"); redirect("/"); }

export async function deleteAccountAction(f: FormData) {
  const u = await currentUser(); if (!u) redirect("/signin");
  if (String(f.get("confirm") ?? "").trim().toLowerCase() !== u.email) redirect("/account?delete=mismatch");
  await deleteAccount(u.id); redirect("/?deleted=1");
}

// ---------- customer ----------
const BookingInput = z.object({
  kind: z.enum(["service", "equipment"]), itemId: z.string().min(1).max(40),
  startsOn: date, endsOn: z.union([date, z.literal("")]).optional(),
  name: z.string().trim().min(2, "Enter your name.").max(80), phone, note: z.string().max(500).optional().default(""),
});

export async function requestBooking(_: FormState, f: FormData): Promise<FormState> {
  const fields = fieldsOf(f);
  if (await limited("booking", 20, 3600_000)) return { error: "Too many requests. Try again later.", fields };
  const p = BookingInput.safeParse(fields);
  if (!p.success) return { error: first(p.error), fields };
  const today = new Date().toISOString().slice(0, 10);
  if (p.data.startsOn < today) return { error: "That date has passed. Choose a future date.", fields };
  const user = await currentUser();
  const r = await data.createBooking({ itemKind: p.data.kind, itemId: p.data.itemId, startsOn: p.data.startsOn, endsOn: p.data.endsOn || p.data.startsOn, customerName: p.data.name, customerPhone: p.data.phone, note: p.data.note, customerId: user?.id ?? null });
  if (!r.ok) return { error: r.error, fields };
  redirect(`/bookings/${r.booking.id}`);
}

// ---------- vendor ----------
const VendorInput = z.object({
  businessName: z.string().trim().min(2, "Enter your business name.").max(80),
  phone: phone.refine(() => true, "Enter a WhatsApp number with country code."),
  cityId: z.string().min(1, "Choose your city."), bio: z.string().max(400).optional().default(""),
});

export async function joinAsVendor(_: FormState, f: FormData): Promise<FormState> {
  const fields = fieldsOf(f);
  const user = await currentUser(); if (!user) redirect("/signin?next=/vendor/join");
  const p = VendorInput.safeParse(fields);
  if (!p.success) return { error: first(p.error), fields };
  if (!(await data.region(p.data.cityId))) return { error: "Choose your city.", fields };
  const valid = new Set((await data.traditions()).map(t => t.id));
  const v = await data.createVendor(user.id, { ...p.data, traditionIds: f.getAll("traditionIds").map(String).filter(t => valid.has(t)) });
  redirect(`/vendor/${v.handle}?welcome=1`);
}

const ListingInput = z.object({
  handle: z.string().min(1), categoryId: z.string().min(1, "Choose a category."),
  title: z.string().trim().min(3, "Give the listing a title.").max(100), description: z.string().max(2000).optional().default(""),
  price: z.coerce.number({ error: "Enter a price above zero." }).positive("Enter a price above zero.").max(100_000_000),
  deposit: z.coerce.number().min(0).max(100_000_000).optional().default(0),
  maxGuests: z.union([z.literal(""), z.coerce.number().int().min(1).max(100000)]).optional(),
  units: z.coerce.number().int().min(1).max(50).optional().default(1),
  included: z.string().max(500).optional().default(""),
});

export async function addListing(_: FormState, f: FormData): Promise<FormState> {
  const fields = fieldsOf(f);
  const user = await currentUser(); if (!user) return { error: "Your session ended. Sign in again." };
  const p = ListingInput.safeParse(fields);
  if (!p.success) return { error: first(p.error), fields };
  const vendor = await data.vendorByHandle(p.data.handle);
  if (!vendor || vendor.ownerId !== user.id) return { error: "You can only add listings to your own business." };
  const cat = (await data.categories()).find(c => c.id === p.data.categoryId);
  if (!cat) return { error: "Choose a category.", fields };
  const price = Math.round(p.data.price * 100);
  if (cat.kind === "service") {
    const max = typeof p.data.maxGuests === "number" ? p.data.maxGuests : null;
    await data.addService(vendor.id, user.id, { categoryId: cat.id, title: p.data.title, description: p.data.description, included: p.data.included.split(",").map(s => s.trim()).filter(Boolean).slice(0, 20), priceMinor: price, priceUnit: "event", minGuests: null, maxGuests: max, advancePct: 30, styles: max && max <= 50 ? ["intimate"] : [], traditionIds: vendor.traditionIds });
  } else {
    await data.addEquipment(vendor.id, user.id, { categoryId: cat.id, title: p.data.title, description: p.data.description, specs: {}, dayRateMinor: price, depositMinor: Math.round(p.data.deposit * 100), needsOperator: f.get("needsOperator") === "on", units: p.data.units });
  }
  revalidatePath(`/vendor/${vendor.handle}`);
  return { ok: true, fields: {} };
}

export async function decideBooking(f: FormData) {
  const user = await currentUser(); if (!user) redirect("/signin");
  const d = String(f.get("decision")); const handle = String(f.get("handle"));
  if (d === "accepted" || d === "declined") await data.setBookingStatus(String(f.get("bookingId")), user.id, d);
  revalidatePath(`/vendor/${handle}`);
}
