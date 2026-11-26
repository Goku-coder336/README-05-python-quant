import Link from "next/link";
export default function NotFound() {
  return (
    <div className="mx-auto max-w-xl px-4 py-24 text-center">
      <p className="eyebrow">Page not found</p>
      <h1 className="mt-3 font-display text-4xl">This page has wandered off</h1>
      <p className="mt-3 text-muted">The link may be old, or the listing was removed.</p>
      <Link href="/explore" className="btn-primary mt-8">Browse cities</Link>
    </div>
  );
}
