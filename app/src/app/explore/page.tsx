export const dynamic = "force-dynamic";
import Link from "next/link";
import { MapPin } from "@phosphor-icons/react/dist/ssr";
import { cities, countries, region } from "@/lib/data";

export const metadata = { title: "Choose your city" };

export default function Explore() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-12 md:px-8 md:py-20">
      <p className="eyebrow">Where is your event?</p>
      <h1 className="mt-3 font-display text-4xl md:text-6xl">Choose a city</h1>
      <p className="mt-4 max-w-xl text-lg text-muted">Every city has its own vendors, prices in local currency and ceremony plans.</p>
      <div className="mt-12 grid gap-12">
        {countries().map(c => {
          const list = cities(c.code);
          return (
            <section key={c.code} aria-labelledby={`c-${c.code}`}>
              <div className="flex items-baseline justify-between gap-4 border-b border-line pb-3">
                <h2 id={`c-${c.code}`} className="font-display text-2xl">{c.name}</h2>
                <span className="text-sm text-muted">{c.currency} · {c.taxName}</span>
              </div>
              {!c.active || list.length === 0 ? (
                <p className="mt-4 text-muted">Coming later. Join the waitlist on the home page to tell us you are here.</p>
              ) : (
                <ul className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
                  {list.map(city => (
                    <li key={city.id}>
                      <Link href={`/${c.code.toLowerCase()}/${city.slug}`} className="card flex items-center gap-3 p-4 transition hover:-translate-y-0.5 hover:border-brown">
                        <MapPin size={20} className="text-brown" aria-hidden />
                        <span><span className="block font-medium">{city.name}</span><span className="text-xs text-muted">{region(city.parentId!)?.name}</span></span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          );
        })}
      </div>
    </div>
  );
}
