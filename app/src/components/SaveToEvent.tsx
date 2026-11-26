"use client";
import { useActionState } from "react";
import Link from "next/link";
import { BookmarkSimple } from "@phosphor-icons/react";
import { saveToEventAction, type FormState } from "@/app/actions";

export function SaveToEvent({ itemKind, itemId, events, signedIn, next }: { itemKind: "service" | "equipment"; itemId: string; events: { id: string; title: string }[]; signedIn: boolean; next: string }) {
  const [state, action, pending] = useActionState<FormState, FormData>(saveToEventAction, {});
  if (!signedIn) return <Link href={`/signin?next=${encodeURIComponent(next)}`} className="btn-line w-full"><BookmarkSimple size={16} aria-hidden />Sign in to save to your event</Link>;
  if (events.length === 0) return <Link href="/plan" className="btn-line w-full"><BookmarkSimple size={16} aria-hidden />Start an event plan to save this</Link>;
  return (
    <form action={action} className="grid gap-2">
      <input type="hidden" name="itemKind" value={itemKind} /><input type="hidden" name="itemId" value={itemId} />
      <div className="flex gap-2">
        <label htmlFor="save-ev" className="sr-only">Event</label>
        <select id="save-ev" name="eventId" className="input !h-11 flex-1 !rounded-full text-sm" defaultValue={state.fields?.eventId ?? events[0].id}>{events.map(e => <option key={e.id} value={e.id}>{e.title}</option>)}</select>
        <button className="btn-line !py-2" disabled={pending}><BookmarkSimple size={16} weight={state.ok ? "fill" : "regular"} aria-hidden />{pending ? "Saving…" : state.ok ? "Saved" : "Save"}</button>
      </div>
      {state.ok && <p role="status" className="text-sm text-success">Saved to your shortlist. <Link className="underline" href={`/my/events/${state.fields?.eventId}`}>Open your plan</Link></p>}
      {state.error && <p role="alert" className="text-sm text-danger">{state.error}</p>}
    </form>
  );
}
