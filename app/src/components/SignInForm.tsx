"use client";
import { useActionState } from "react";
import { checkCode, sendCode, type FormState } from "@/app/actions";

export function SignInForm({ next }: { next: string }) {
  const [sent, send, sending] = useActionState<FormState, FormData>(sendCode, {});
  const [checked, check, checking] = useActionState<FormState, FormData>(checkCode, {});
  const email = sent.fields?.email ?? "";
  if (sent.step !== "code") return (
    <form action={send} className="grid gap-4" noValidate>
      <div><label className="label" htmlFor="email">Email</label><input className="input" id="email" name="email" type="email" autoComplete="email" defaultValue={email} required autoFocus /></div>
      {sent.error && <p role="alert" className="rounded-2xl bg-blush px-4 py-3 text-sm text-danger">{sent.error}</p>}
      <button className="btn-primary" disabled={sending}>{sending ? "Sending code…" : "Email me a sign-in code"}</button>
      <p className="text-center text-xs text-muted">No password needed. We send a 6-digit code.</p>
    </form>
  );
  return (
    <form action={check} className="grid gap-4" noValidate>
      <p role="status" className="text-sm">We sent a code to <strong>{email}</strong>. It expires in 10 minutes.</p>
      <input type="hidden" name="email" value={email} /><input type="hidden" name="next" value={next} />
      <div><label className="label" htmlFor="code">6-digit code</label><input className="input text-center font-mono text-2xl tracking-[.5em]" id="code" name="code" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6} required autoFocus /></div>
      {checked.error && <p role="alert" className="rounded-2xl bg-blush px-4 py-3 text-sm text-danger">{checked.error}</p>}
      <button className="btn-primary" disabled={checking}>{checking ? "Checking…" : "Sign in"}</button>
    </form>
  );
}
