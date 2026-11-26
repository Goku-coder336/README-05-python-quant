import Link from "next/link";
import { overview, recentLog, waitlistByCity } from "@/lib/admin";
export default async function AdminHome() {
  const [o, cities, log] = await Promise.all([overview(), waitlistByCity(), recentLog()]);
  const stats: [string, number, string?][] = [["Vendors waiting for review", o.pending, "/admin/vendors"], ["Vendors", o.vendors], ["Accounts", o.customers], ["Event plans", o.events], ["Bookings", o.bookings], ["Waitlist sign-ups", o.waitlist, "/admin/waitlist"]];
  return (
    <div className="grid gap-10">
      <h1 className="font-display text-4xl">Overview</h1>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
        {stats.map(([k, n, href]) => {
          const body = <><p className="text-xs text-muted">{k}</p><p className="mt-1 font-display text-4xl">{n}</p></>;
          return href ? <Link key={k} href={href} className={`card p-5 transition hover:border-brown ${k.startsWith("Vendors waiting") && n > 0 ? "border-caramel bg-sand" : ""}`}>{body}</Link> : <div key={k} className="card p-5">{body}</div>;
        })}
      </div>
      <section aria-labelledby="dem"><h2 id="dem" className="font-display text-2xl">Where demand is</h2><p className="mt-1 text-sm text-muted">Waitlist by city. Open the next city where both columns are strong.</p>
        {cities.length === 0 ? <p className="mt-4 text-muted">No sign-ups yet.</p> :
          <ul className="mt-4 grid gap-2">{cities.slice(0, 8).map(c => {
            const max = cities[0].total;
            return <li key={c.city} className="grid grid-cols-[120px_1fr_auto] items-center gap-3 text-sm"><span className="font-medium">{c.city}</span>
              <span className="flex h-3 overflow-hidden rounded-full bg-sand" aria-hidden><span className="bg-brown" style={{ width: `${(c.customers / max) * 100}%` }} /><span className="bg-caramel" style={{ width: `${(c.vendors / max) * 100}%` }} /></span>
              <span className="text-muted">{c.customers} customers · {c.vendors} vendors</span></li>;
          })}</ul>}
      </section>
      <section aria-labelledby="log"><h2 id="log" className="font-display text-2xl">Recent admin actions</h2>
        {log.length === 0 ? <p className="mt-2 text-muted">Nothing yet.</p> : <ul className="mt-3 divide-y divide-line text-sm">{log.map((l, i) => <li key={i} className="flex flex-wrap justify-between gap-2 py-2"><span><code className="text-xs">{l.action}</code> · {l.target}</span><span className="text-muted">{l.email} · {new Date(l.createdAt).toLocaleString("en-GB")}</span></li>)}</ul>}
      </section>
    </div>
  );
}
