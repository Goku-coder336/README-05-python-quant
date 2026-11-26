"use server";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { z } from "zod";
import * as data from "@/lib/data";
import * as planner from "@/lib/planner";
import * as media from "@/lib/media";
import { notifyBooking } from "@/lib/notify";
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
  eventItemId: z.string().max(40).optional().default(""),
});

export async function requestBooking(_: FormState, f: FormData): Promise<FormState> {
  const fields = fieldsOf(f);
  if (await limited("booking", 20, 3600_000)) return { error: "Too many requests. Try again later.", fields };
  const p = BookingInput.safeParse(fields);
  if (!p.success) return { error: first(p.error), fields };
  const today = new Date().toISOString().slice(0, 10);
  if (p.data.startsOn < today) return { error: "That date has passed. Choose a future date.", fields };
  const user = await currentUser();
  if (!user) return { error: "Sign in to send a booking request, so we can tell you when the vendor replies.", fields };
  // Only link the booking to a checklist item the signed-in customer owns.
  const eventItemId = p.data.eventItemId ? (await planner.ownedItemForBooking(p.data.eventItemId, user.id))?.id ?? null : null;
  const r = await data.createBooking({ eventItemId, itemKind: p.data.kind, itemId: p.data.itemId, startsOn: p.data.startsOn, endsOn: p.data.endsOn || p.data.startsOn, customerName: p.data.name, customerPhone: p.data.phone, note: p.data.note, customerId: user.id });
  if (!r.ok) return { error: r.error, fields };
  await notifyBooking(r.booking.id, ["booking.requested.vendor", "booking.requested.customer"]);
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
  const bookingId = String(f.get("bookingId"));
  if ((d === "accepted" || d === "declined") && await data.setBookingStatus(bookingId, user.id, d)) await notifyBooking(bookingId, [d === "accepted" ? "booking.accepted" : "booking.declined"]);
  revalidatePath(`/vendor/${handle}`);
}

// ---------- event planner ----------
const EventInput = z.object({
  eventTypeId: z.string().min(1, "Choose what you are planning."),
  traditionId: z.string().optional().default(""),
  cityId: z.string().min(1, "Choose the city."),
  title: z.string().trim().min(2, "Give your event a name, for example Anu and Joel's wedding.").max(80),
  guestCount: z.union([z.literal(""), z.coerce.number().int().min(1, "Guests must be at least 1.").max(20000)]).optional().default(""),
  budget: z.union([z.literal(""), z.coerce.number().min(0).max(1_000_000_000)]).optional().default(""),
  eventDate: z.union([z.literal(""), z.string().regex(/^\d{4}-\d{2}-\d{2}$/)]).optional().default(""),
});

export async function createEventAction(_: FormState, f: FormData): Promise<FormState> {
  const fields = fieldsOf(f);
  const user = await currentUser(); if (!user) redirect("/signin?next=/plan");
  const p = EventInput.safeParse(fields);
  if (!p.success) return { error: first(p.error), fields };
  if (p.data.eventDate && p.data.eventDate < new Date().toISOString().slice(0, 10)) return { error: "That date has passed. Choose a future date or leave it empty.", fields };
  const types = await planner.eventTypes(); if (!types.some(t => t.id === p.data.eventTypeId)) return { error: "Choose what you are planning.", fields };
  const trads = await data.traditions(); const traditionId = trads.some(t => t.id === p.data.traditionId) ? p.data.traditionId : null;
  if (!(await data.region(p.data.cityId))) return { error: "Choose the city.", fields };
  const ev = await planner.createEvent(user.id, { eventTypeId: p.data.eventTypeId, traditionId, cityId: p.data.cityId, title: p.data.title,
    guestCount: typeof p.data.guestCount === "number" ? p.data.guestCount : null, budgetMinor: typeof p.data.budget === "number" ? Math.round(p.data.budget * 100) : null,
    eventDate: p.data.eventDate || null });
  if (!ev) return { error: "Could not create the event. Try again.", fields };
  redirect(`/my/events/${ev.id}`);
}

const Status = z.enum(["todo", "shortlisted", "booked", "skipped"]);
export async function setItemStatusAction(f: FormData) {
  const user = await currentUser(); if (!user) redirect("/signin");
  const st = Status.safeParse(f.get("status")); if (!st.success || st.data === "booked") return;
  await planner.setItemStatus(String(f.get("itemId")), user.id, st.data);
  revalidatePath(`/my/events/${String(f.get("eventId"))}`);
}

export async function addItemAction(_: FormState, f: FormData): Promise<FormState> {
  const user = await currentUser(); if (!user) redirect("/signin");
  const label = String(f.get("label") ?? "").trim(); const categoryId = String(f.get("categoryId") ?? ""); const eventId = String(f.get("eventId"));
  if (label.length < 2) return { error: "Name the item, for example Welcome drinks." };
  if (!(await data.categories()).some(c => c.id === categoryId)) return { error: "Choose a category." };
  await planner.addItem(eventId, user.id, { categoryId, label: label.slice(0, 80), subEvent: String(f.get("subEvent") || "Added by you").slice(0, 40) });
  revalidatePath(`/my/events/${eventId}`); return { ok: true };
}

export async function removeItemAction(f: FormData) {
  const user = await currentUser(); if (!user) redirect("/signin");
  await planner.removeItem(String(f.get("itemId")), user.id); revalidatePath(`/my/events/${String(f.get("eventId"))}`);
}

const Kind = z.enum(["service", "equipment"]);
export async function saveToEventAction(_: FormState, f: FormData): Promise<FormState> {
  const user = await currentUser(); if (!user) return { error: "Sign in to save to an event." };
  const k = Kind.safeParse(f.get("itemKind")); if (!k.success) return { error: "Something went wrong." };
  const r = await planner.saveToEvent(String(f.get("eventId")), user.id, k.data, String(f.get("itemId")));
  return r ? { ok: true, fields: { eventId: String(f.get("eventId")) } } : { error: "Could not save to that event." };
}

export async function unsaveAction(f: FormData) {
  const user = await currentUser(); if (!user) redirect("/signin");
  const k = Kind.safeParse(f.get("itemKind")); if (!k.success) return;
  await planner.unsave(String(f.get("eventItemId")), user.id, k.data, String(f.get("itemId")));
  revalidatePath(`/my/events/${String(f.get("eventId"))}`);
}

export async function deleteEventAction(f: FormData) {
  const user = await currentUser(); if (!user) redirect("/signin");
  await planner.deleteEvent(String(f.get("eventId")), user.id); redirect("/my/events");
}

// ---------- photos ----------
export type PhotoState = { error?: string; ok?: string };
const Owner = z.enum(["vendor", "service", "equipment"]);

export async function uploadPhotosAction(_: PhotoState, f: FormData): Promise<PhotoState> {
  const user = await currentUser(); if (!user) return { error: "Your session ended. Sign in again." };
  if (await limited("upload", 60, 3600_000)) return { error: "Too many uploads. Try again later." };
  const kind = Owner.safeParse(f.get("kind")); if (!kind.success) return { error: "Something went wrong." };
  const files = f.getAll("photos").filter((x): x is File => x instanceof File && x.size > 0);
  if (!files.length) return { error: "Choose at least one photo." };
  if (files.length > 6) return { error: "Upload up to 6 photos at a time." };
  const r = await media.uploadPhotos(user.id, kind.data, String(f.get("ownerId")), files);
  revalidatePath(`/vendor/${String(f.get("handle"))}`);
  if (!r.added) return { error: r.errors.join(" ") || "No photos were added." };
  return { ok: `${r.added} photo${r.added === 1 ? "" : "s"} added.${r.errors.length ? " " + r.errors.join(" ") : ""}` };
}

export async function deletePhotoAction(f: FormData) {
  const user = await currentUser(); if (!user) redirect("/signin");
  await media.deletePhoto(user.id, String(f.get("mediaId"))); revalidatePath(`/vendor/${String(f.get("handle"))}`);
}

export async function coverPhotoAction(f: FormData) {
  const user = await currentUser(); if (!user) redirect("/signin");
  await media.makeCover(user.id, String(f.get("mediaId"))); revalidatePath(`/vendor/${String(f.get("handle"))}`);
}

export async function cancelBookingAction(f: FormData) {
  const user = await currentUser(); if (!user) redirect("/signin?next=/my/bookings");
  const id = String(f.get("bookingId"));
  if (await data.cancelBooking(id, user.id)) await notifyBooking(id, ["booking.cancelled.vendor"]);
  revalidatePath("/my/bookings"); revalidatePath(`/bookings/${id}`);
}
