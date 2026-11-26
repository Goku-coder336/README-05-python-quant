export const dynamic = "force-dynamic";
import { cities, countries, region, traditions } from "@/lib/data";
import { JoinForm } from "@/components/JoinForm";

export const metadata = { title: "List your business" };

export default function Join() {
  const list = cities().map(c => ({ id: c.id, name: c.name, group: `${region(c.parentId!)?.name}, ${countries().find(x => x.code === c.countryCode)?.name}` }));
  return (
    <div className="mx-auto grid max-w-6xl gap-12 px-4 py-12 md:px-8 lg:grid-cols-2 lg:py-20">
      <div>
        <p className="eyebrow">For vendors and rental owners</p>
        <h1 className="mt-3 font-display text-4xl md:text-6xl">Get found by people ready to book</h1>
        <ul className="mt-8 grid gap-4 text-lg">
          <li>Free profile for your services and packages</li>
          <li>List gear with a day rate, deposit and calendar</li>
          <li>Requests arrive on WhatsApp and your dashboard</li>
        </ul>
      </div>
      <div className="card p-6 md:p-8"><JoinForm cities={list} traditions={traditions()} /></div>
    </div>
  );
}
