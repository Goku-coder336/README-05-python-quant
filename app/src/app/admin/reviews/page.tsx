import { latestReviews } from "@/lib/reviews";
import { Stars } from "@/components/Stars";
import { hideReviewAction } from "../actions";
export const metadata = { title: "Reviews" };
export default async function AdminReviews() {
  const list = await latestReviews();
  return (
    <div>
      <h1 className="font-display text-4xl">Reviews</h1>
      <p className="mt-2 max-w-2xl text-muted">Hide only reviews that break the rules (abuse, personal details, spam, or not about the booking). Low ratings that are honest stay up. Hidden reviews stop counting towards the vendor&apos;s average.</p>
      {list.length === 0 ? <div className="card mt-6 p-10 text-center text-muted">No reviews yet.</div> :
        <ul className="mt-6 grid gap-3">{list.map(r => (
          <li key={r.id} className={`card p-5 ${r.hidden ? "opacity-60" : ""}`}>
            <div className="flex flex-wrap items-center justify-between gap-2"><span className="flex items-center gap-2"><Stars value={r.rating} /><span className="font-medium">{r.authorName}</span><span className="text-sm text-muted">for {r.vendorName}</span></span>
              {r.hidden && <span className="badge bg-blush text-danger">Hidden: {r.hiddenReason}</span>}</div>
            {r.body && <p className="mt-2 text-sm">{r.body}</p>}
            <form action={hideReviewAction} className="mt-3 flex flex-wrap items-end gap-2"><input type="hidden" name="reviewId" value={r.id} />
              {r.hidden ? <button name="hidden" value="0" className="btn-line !py-2">Show again</button> : <>
                <label className="sr-only" htmlFor={`why-${r.id}`}>Reason</label>
                <select id={`why-${r.id}`} name="reason" className="input !h-10 !w-auto text-sm"><option>Abusive or hateful</option><option>Contains personal details</option><option>Spam or advertising</option><option>Not about this booking</option></select>
                <button name="hidden" value="1" className="btn-line !py-2">Hide</button></>}
            </form>
          </li>))}</ul>}
    </div>
  );
}
