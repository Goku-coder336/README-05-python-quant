import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
export const metadata = { title: { default: "Admin", template: "%s | Festora admin" }, robots: { index: false } };
const nav = [["/admin", "Overview"], ["/admin/vendors", "Vendors"], ["/admin/waitlist", "Waitlist"], ["/admin/templates", "Checklists"]];
export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const a = await requireAdmin();
  return (
    <div className="mx-auto max-w-6xl px-4 py-8 md:px-8">
      <div className="flex flex-wrap items-center justify-between gap-3"><p className="eyebrow">Admin · {a.email}</p></div>
      <nav aria-label="Admin" className="mt-3 flex gap-2 overflow-x-auto border-b border-line pb-3">
        {nav.map(([href, label]) => <Link key={href} href={href} className="chip shrink-0">{label}</Link>)}
      </nav>
      <div className="py-8">{children}</div>
    </div>
  );
}
