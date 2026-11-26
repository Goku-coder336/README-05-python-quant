import { SealCheck } from "@phosphor-icons/react/dist/ssr";
import type { Review } from "@/lib/reviews";
import { Stars } from "./Stars";
export function ReviewList({ reviews, vendorName, empty }: { reviews: Review[]; vendorName: string; empty: string }) {
  if (!reviews.length) return <p className="mt-3 text-muted">{empty}</p>;
  return (
    <ul className="mt-4 grid gap-3">{reviews.map(r => (
      <li key={r.id} className="card p-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="flex items-center gap-2"><Stars value={r.rating} /><span className="font-medium">{r.authorName}</span></span>
          <span className="text-xs text-muted">{new Date(r.createdAt).toLocaleDateString("en-GB", { month: "long", year: "numeric" })}</span>
        </div>
        <p className="mt-1 flex items-center gap-1 text-xs text-success"><SealCheck size={14} weight="fill" aria-hidden />Booked {r.itemTitle} on Utsella</p>
        {r.body && <p className="mt-3 whitespace-pre-line">{r.body}</p>}
        {r.vendorReply && <div className="mt-4 rounded-2xl bg-sand p-4 text-sm"><p className="font-medium">Reply from {vendorName}</p><p className="mt-1 whitespace-pre-line text-muted">{r.vendorReply}</p></div>}
      </li>))}</ul>
  );
}
