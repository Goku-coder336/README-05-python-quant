import { currentUser } from "@/lib/auth";
import { waitlistRows } from "@/lib/admin";
const cell = (v: string) => /^[=+\-@]/.test(v) ? `"'${v.replace(/"/g, '""')}"` : `"${v.replace(/"/g, '""')}"`; // blocks spreadsheet formula injection
export async function GET() {
  const u = await currentUser();
  if (!u || u.role !== "admin") return new Response("Not found", { status: 404 });
  const rows = await waitlistRows();
  const csv = ["email,role,city,signed_up", ...rows.map(r => [r.email, r.role, r.city, new Date(r.createdAt).toISOString()].map(cell).join(","))].join("\n");
  return new Response(csv, { headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="utsella-waitlist-${new Date().toISOString().slice(0, 10)}.csv"`, "Cache-Control": "no-store" } });
}
