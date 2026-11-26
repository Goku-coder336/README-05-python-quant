"use client";
import { useActionState, useEffect, useRef } from "react";
import type { CatState } from "@/app/admin/actions";
// Small wrapper so admin forms show their own error or success message and reset after success.
export function AdminForm({ action, children, submit, className }: { action: (s: CatState, f: FormData) => Promise<CatState>; children: React.ReactNode; submit: string; className?: string }) {
  const [state, run, pending] = useActionState<CatState, FormData>(action, {});
  const ref = useRef<HTMLFormElement>(null);
  useEffect(() => { if (state.ok) ref.current?.reset(); }, [state]);
  return (
    <form ref={ref} action={run} className={className ?? "grid gap-3 sm:grid-cols-[1fr_1fr_1fr_auto] sm:items-end"} noValidate>
      {children}
      <button className="btn-primary !py-2.5" disabled={pending}>{pending ? "Saving…" : submit}</button>
      {state.error && <p role="alert" className="text-sm text-danger sm:col-span-full">{state.error}</p>}
      {state.ok && <p role="status" className="text-sm text-success sm:col-span-full">{state.ok}</p>}
    </form>
  );
}
