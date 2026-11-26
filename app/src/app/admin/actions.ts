"use server";
import { revalidatePath } from "next/cache";
import { z } from "zod";
import * as admin from "@/lib/admin";
import { categories } from "@/lib/data";
import { ICON_CHOICES } from "@/components/Icon";
import { redirect } from "next/navigation";

export async function verifyVendorAction(f: FormData) {
  const a = await admin.requireAdmin();
  const verified = f.get("verified") === "1";
  await admin.setVerification(a.id, String(f.get("vendorId")), verified, String(f.get("note") ?? "").slice(0, 300));
  revalidatePath("/admin/vendors"); revalidatePath("/admin");
}

const Item = z.object({
  id: z.union([z.literal(""), z.coerce.number().int().positive()]).optional(),
  categoryId: z.string().min(1, "Choose a category."), subEvent: z.string().trim().min(1, "Add the part of the day.").max(40),
  label: z.string().trim().min(2, "Add a label.").max(80), note: z.string().trim().max(120).optional().default(""),
  budgetShare: z.coerce.number().int().min(0).max(100).optional().default(0), sort: z.coerce.number().int().min(0).max(999).optional().default(0),
});
export type ItemState = { error?: string; ok?: boolean };

export async function saveItemAction(_: ItemState, f: FormData): Promise<ItemState> {
  const a = await admin.requireAdmin(); const templateId = String(f.get("templateId"));
  const p = Item.safeParse(Object.fromEntries(f.entries()));
  if (!p.success) return { error: p.error.issues[0]?.message };
  if (!(await categories()).some(c => c.id === p.data.categoryId)) return { error: "Choose a category." };
  await admin.saveTemplateItem(a.id, templateId, { ...p.data, id: typeof p.data.id === "number" ? p.data.id : undefined });
  revalidatePath(`/admin/templates/${templateId}`); return { ok: true };
}

export async function deleteItemAction(f: FormData) {
  const a = await admin.requireAdmin(); const templateId = String(f.get("templateId"));
  await admin.deleteTemplateItem(a.id, templateId, Number(f.get("itemId")));
  revalidatePath(`/admin/templates/${templateId}`);
}

// ---------- catalogue ----------
export type CatState = { error?: string; ok?: string };
const Name = z.string().trim().min(2, "Enter a name.").max(60);
const IconName = z.enum(ICON_CHOICES);
const GROUPS = ["Weddings and family", "Religious and cultural", "Parties and celebrations", "Business and professional", "Community and public", "Something else"] as const;

export async function createEventTypeAction(_: CatState, f: FormData): Promise<CatState> {
  const a = await admin.requireAdmin();
  const p = z.object({ name: Name, grp: z.enum(GROUPS), icon: IconName }).safeParse(Object.fromEntries(f.entries()));
  if (!p.success) return { error: p.error.issues[0]?.message };
  const r = await admin.createEventType(a.id, p.data); if ("error" in r) return { error: r.error };
  revalidatePath("/admin/catalogue"); redirect(`/admin/templates/${r.templateId}?new=1`);
}
export async function createCategoryAction(_: CatState, f: FormData): Promise<CatState> {
  const a = await admin.requireAdmin();
  const p = z.object({ name: Name, kind: z.enum(["service", "equipment"]), icon: IconName }).safeParse(Object.fromEntries(f.entries()));
  if (!p.success) return { error: p.error.issues[0]?.message };
  const r = await admin.createCategory(a.id, p.data); if ("error" in r) return { error: r.error };
  revalidatePath("/admin/catalogue"); return { ok: `${p.data.name} added. Vendors can now list under it.` };
}
export async function createTraditionAction(_: CatState, f: FormData): Promise<CatState> {
  const a = await admin.requireAdmin();
  const p = Name.safeParse(f.get("name")); if (!p.success) return { error: p.error.issues[0]?.message };
  const r = await admin.createTradition(a.id, p.data); if ("error" in r) return { error: r.error };
  revalidatePath("/admin/catalogue"); return { ok: `${p.data} added.` };
}
export async function toggleActiveAction(f: FormData) {
  const a = await admin.requireAdmin();
  const what = z.enum(["event_type", "category", "tradition"]).parse(f.get("what"));
  await admin.setActive(a.id, what, String(f.get("id")), f.get("active") === "1"); revalidatePath("/admin/catalogue");
}
export async function createTemplateAction(_: CatState, f: FormData): Promise<CatState> {
  const a = await admin.requireAdmin();
  const p = z.object({ eventTypeId: z.string().min(1, "Choose an occasion."), traditionId: z.string().optional().default(""), sizeTier: z.enum(["standard", "intimate"]), copyFrom: z.string().optional().default("") }).safeParse(Object.fromEntries(f.entries()));
  if (!p.success) return { error: p.error.issues[0]?.message };
  const r = await admin.createTemplate(a.id, { eventTypeId: p.data.eventTypeId, traditionId: p.data.traditionId || null, sizeTier: p.data.sizeTier, copyFrom: p.data.copyFrom || null });
  if ("error" in r) return { error: r.error };
  redirect(`/admin/templates/${r.id}?new=1`);
}
