import Link from "next/link";
import { notFound } from "next/navigation";
import { categories, category as getCategory, city as getCity, country as getCountry, listings, traditions } from "@/lib/data";
import { CategoryIcon } from "./Icon";
import { ListingCard } from "./ListingCard";

type SP = { intimate?: string; tradition?: string };

export async function CityListings({ countryCode, citySlug, categorySlug, sp }: { countryCode: string; citySlug: string; categorySlug?: string; sp: SP }) {
  const [ctry, city] = await Promise.all([getCountry(countryCode), getCity(countryCode, citySlug)]);
  if (!ctry || !city) notFound();
  const cat = categorySlug ? await getCategory(categorySlug) : null;
  if (categorySlug && !cat) notFound();
  const allTrads = await traditions(); const allCats = await categories();
  const trad = allTrads.find(t => t.slug === sp.tradition);
  const intimate = sp.intimate === "1";
  const items = await listings({ cityId: city.id, categoryId: cat?.id, intimate, traditionId: trad?.id });
  const base = `/${countryCode}/${citySlug}`;
  const here = cat ? `${base}/${cat.slug}` : base;
  const q = (next: Partial<SP>) => {
    const p = new URLSearchParams();
    const merged = { intimate: sp.intimate, tradition: sp.tradition, ...next };
    if (merged.intimate === "1") p.set("intimate", "1");
    if (merged.tradition) p.set("tradition", merged.tradition);
    const s = p.toString(); return s ? `?${s}` : "";
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 md:px-8 md:py-16">
      <nav aria-label="Breadcrumb" className="text-sm text-muted"><Link href="/explore" className="hover:underline">{ctry.name}</Link> / <Link href={base} className="hover:underline">{city.name}</Link>{cat && <> / {cat.name}</>}</nav>
      <h1 className="mt-3 font-display text-4xl md:text-5xl">{cat ? `${cat.name} in ${city.name}` : `Plan your event in ${city.name}`}</h1>

      <div className="mt-8 flex gap-2 overflow-x-auto pb-2" role="list" aria-label="Categories">
        <Link role="listitem" href={`${base}${q({})}`} className={!cat ? "chip-on" : "chip"} aria-current={!cat ? "page" : undefined}>All</Link>
        {allCats.map(c => (
          <Link role="listitem" key={c.id} href={`${base}/${c.slug}${q({})}`} className={`${cat?.id === c.id ? "chip-on" : "chip"} shrink-0`} aria-current={cat?.id === c.id ? "page" : undefined}>
            <CategoryIcon name={c.icon} size={16} />{c.name}
          </Link>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
        <span className="text-muted">Filter:</span>
        <Link href={`${here}${q({ intimate: intimate ? undefined : "1" })}`} className={intimate ? "chip-on" : "chip"} aria-pressed={intimate}>Intimate, up to 50 guests</Link>
        {allTrads.map(t => (
          <Link key={t.id} href={`${here}${q({ tradition: trad?.id === t.id ? undefined : t.slug })}`} className={trad?.id === t.id ? "chip-on" : "chip"} aria-pressed={trad?.id === t.id}>{t.name}</Link>
        ))}
      </div>

      <p className="mt-8 text-sm text-muted" aria-live="polite">{items.length} {items.length === 1 ? "result" : "results"}</p>
      {items.length === 0 ? (
        <div className="card mt-4 p-10 text-center">
          <h2 className="font-display text-2xl">Nothing here yet</h2>
          <p className="mx-auto mt-2 max-w-md text-muted">No {cat ? cat.name.toLowerCase() : "vendors"} match these filters in {city.name} so far. Clear a filter, or try a nearby city.</p>
          <div className="mt-6 flex flex-wrap justify-center gap-3"><Link href={here} className="btn-primary">Clear filters</Link><Link href="/explore" className="btn-line">Other cities</Link></div>
        </div>
      ) : (
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map(l => <div key={l.item.id} className="relative"><ListingCard l={l} /></div>)}
        </div>
      )}
    </div>
  );
}
