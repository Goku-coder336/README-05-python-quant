"use client";
import { useActionState, useRef, useEffect } from "react";
import { addBlockAction, type BlockState } from "@/app/actions";
export function BlockForm({ vendorId, handle, today }: { vendorId: string; handle: string; today: string }) {
  const [state, action, pending] = useActionState<BlockState, FormData>(addBlockAction, {});
  const ref = useRef<HTMLFormElement>(null);
  useEffect(() => { if (state.ok) ref.current?.reset(); }, [state]);
  return (
    <form ref={ref} action={action} className="grid gap-3" noValidate>
      <input type="hidden" name="vendorId" value={vendorId} /><input type="hidden" name="handle" value={handle} />
      <div className="grid grid-cols-2 gap-3">
        <label className="grid min-w-0 gap-1 text-sm font-medium">From<input type="date" name="from" min={today} required className="input min-w-0" /></label>
        <label className="grid min-w-0 gap-1 text-sm font-medium">To <span className="sr-only">(optional, same day if empty)</span><input type="date" name="to" min={today} className="input min-w-0" /></label>
      </div>
      <label className="grid gap-1 text-sm font-medium">Note for yourself <span className="font-normal text-muted">(optional, not shown to customers)</span><input name="note" maxLength={120} className="input" placeholder="Family wedding" /></label>
      {state.error && <p role="alert" className="text-sm text-danger">{state.error}</p>}
      {state.ok && <p role="status" className="text-sm text-success">Blocked. Customers cannot request those days.</p>}
      <button className="btn-primary w-fit !py-2" disabled={pending}>{pending ? "Saving…" : "Block these days"}</button>
    </form>
  );
}
