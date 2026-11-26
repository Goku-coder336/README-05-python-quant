import { waitlistByCity, waitlistRows } from "@/lib/admin";
export const metadata = { title: "Waitlist" };
export default async function AdminWaitlist() {
  const [cities, rows] = await Promise.all([waitlistByCity(), waitlistRows()]);
  return (
    <div>
      <div className="flex flex-wrap items-end justify-between gap-3"><h1 className="font-display text-4xl">Waitlist</h1><a href="/admin/waitlist/export" className="btn-line">Download CSV</a></div>
      <div className="card mt-6 overflow-x-auto"><table className="w-full text-left text-sm">
        <caption className="sr-only">Sign-ups by city</caption>
        <thead className="border-b border-line text-muted"><tr><th scope="col" className="p-4 font-medium">City</th><th scope="col" className="p-4 font-medium">Customers</th><th scope="col" className="p-4 font-medium">Vendors</th><th scope="col" className="p-4 font-medium">Total</th></tr></thead>
        <tbody>{cities.length === 0 ? <tr><td colSpan={4} className="p-6 text-center text-muted">No sign-ups yet.</td></tr> : cities.map(c => <tr key={c.city} className="border-b border-line last:border-0"><th scope="row" className="p-4 font-medium">{c.city}</th><td className="p-4">{c.customers}</td><td className="p-4">{c.vendors}</td><td className="p-4 font-semibold">{c.total}</td></tr>)}</tbody>
      </table></div>
      <h2 className="mt-10 font-display text-2xl">Latest sign-ups</h2>
      <ul className="mt-3 divide-y divide-line text-sm">{rows.slice(0, 50).map(r => <li key={r.email + r.role} className="flex flex-wrap justify-between gap-2 py-2"><span>{r.email}</span><span className="text-muted">{r.role} · {r.city} · {new Date(r.createdAt).toLocaleDateString("en-GB")}</span></li>)}</ul>
    </div>
  );
}
