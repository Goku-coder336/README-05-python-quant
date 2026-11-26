"use server";
import { revalidatePath } from "next/cache";
import { z } from "zod";
import * as admin from "@/lib/admin";
import { categories } from "@/lib/data";

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
