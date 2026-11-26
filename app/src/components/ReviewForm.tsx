"use client";
import { useActionState, useState } from "react";
import { reviewAction, type ReviewState } from "@/app/actions";
const words = ["", "Poor", "Below expectations", "Good", "Very good", "Excellent"];
export function ReviewForm({ bookingId, vendorName, starIcons }: { bookingId: string; vendorName: string; starIcons: { on: React.ReactNode; off: React.ReactNode } }) {
  const [state, action, pending] = useActionState<ReviewState, FormData>(reviewAction, {});
  const [rating, setRating] = useState(0); const [hover, setHover] = useState(0);
  if (state.ok) return <p role="status" className="rounded-2xl bg-sage px-4 py-3 text-sm text-success">Thank you. Your review is live on {vendorName}&apos;s profile.</p>;
  const shown = hover || rating;
  return (
    <form action={action} className="grid gap-3 rounded-2xl bg-sand p-4" noValidate>
      <input type="hidden" name="bookingId" value={bookingId} />
      <fieldset><legend className="text-sm font-medium">How was {vendorName}?</legend>
        <div className="mt-1 flex items-center gap-1" onMouseLeave={() => setHover(0)}>
          {[1, 2, 3, 4, 5].map(n => (
            <label key={n} className="cursor-pointer rounded-md p-0.5 text-caramel has-[:focus-visible]:outline has-[:focus-visible]:outline-2 has-[:focus-visible]:outline-brown" onMouseEnter={() => setHover(n)}>
              <input type="radio" name="rating" value={n} className="sr-only" checked={rating === n} onChange={() => setRating(n)} />
              <span className="sr-only">{n} star{n === 1 ? "" : "s"}, {words[n]}</span>
              {shown >= n ? starIcons.on : starIcons.off}
            </label>
          ))}
          <span className="ml-2 text-sm text-muted" aria-hidden>{words[shown]}</span>
        </div>
      </fieldset>
      <label className="text-sm font-medium" htmlFor={`rv-${bookingId}`}>What should others know? <span className="font-normal text-muted">(optional)</span></label>
      <textarea id={`rv-${bookingId}`} name="body" maxLength={1000} className="input h-24 py-3" placeholder="Arrived early, set up quietly, photos came in two weeks." />
      {state.error && <p role="alert" className="text-sm text-danger">{state.error}</p>}
      <button className="btn-primary w-fit !py-2" disabled={pending || !rating}>{pending ? "Posting…" : "Post review"}</button>
      <p className="text-xs text-muted">Shown with your first name and last initial. Only people who booked can review.</p>
    </form>
  );
}
