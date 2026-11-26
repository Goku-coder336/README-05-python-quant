import Link from "next/link";

// Shared layout for legal pages. {{placeholders}} are facts the business must fill in; they render highlighted.
export const LEGAL_UPDATED = "27 November 2026";

export function LegalPage({ title, intro, children }: { title: string; intro: string; children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 md:py-20">
      <p role="note" className="mb-8 rounded-2xl border border-caramel bg-sand px-4 py-3 text-sm">
        <strong>Draft for legal review.</strong> Highlighted items still need the business&apos;s details. Remove this notice once a lawyer has approved the text.
      </p>
      <p className="eyebrow">Legal</p>
      <h1 className="mt-3 font-display text-4xl md:text-5xl">{title}</h1>
      <p className="mt-2 text-sm text-muted">Last updated {LEGAL_UPDATED}</p>
      <p className="mt-6 text-lg">{intro}</p>
      <div className="legal mt-10 grid gap-8 leading-relaxed [&_h2]:font-display [&_h2]:text-2xl [&_li]:mt-1 [&_p]:mt-3 [&_ul]:mt-3 [&_ul]:list-disc [&_ul]:pl-6">{children}</div>
      <nav aria-label="Legal pages" className="mt-16 flex flex-wrap gap-4 border-t border-line pt-6 text-sm">
        <Link className="underline" href="/legal/terms">Terms</Link><Link className="underline" href="/legal/privacy">Privacy</Link>
        <Link className="underline" href="/legal/refunds">Refunds and cancellations</Link><Link className="underline" href="/contact">Contact and grievances</Link>
      </nav>
    </div>
  );
}

/** A fact the business must supply. */
export function Fill({ children }: { children: React.ReactNode }) {
  return <mark className="rounded bg-caramel/40 px-1 text-ink">{`{{${children}}}`}</mark>;
}
