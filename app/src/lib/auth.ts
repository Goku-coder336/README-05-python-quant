import crypto from "node:crypto";
import { cookies } from "next/headers";
import { one, q } from "./db";

// Passwordless sign-in: a 6-digit code by email, then an http-only session cookie.
// Codes and session tokens are stored only as HMAC hashes.
const COOKIE = "festora_session";
const SESSION_DAYS = 30;
const CODE_MINUTES = 10;
const MAX_CODES_PER_HOUR = 5;
const MAX_ATTEMPTS = 5;

function secret() {
  const s = process.env.SESSION_SECRET;
  if (!s || s.length < 32) throw new Error("SESSION_SECRET must be set (32+ characters).");
  return s;
}
const hash = (v: string) => crypto.createHmac("sha256", secret()).update(v).digest("hex");
export const normaliseEmail = (e: string) => e.trim().toLowerCase();
export const validEmail = (e: string) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e) && e.length <= 254;

export type User = { id: string; email: string; name: string | null; role: "member" | "admin" };

export async function requestCode(emailRaw: string): Promise<{ ok: true } | { ok: false; error: string }> {
  const email = normaliseEmail(emailRaw);
  if (!validEmail(email)) return { ok: false, error: "Enter a valid email address." };
  const recent = await one<{ n: number }>(`select count(*)::int as n from login_codes where email = $1 and created_at > now() - interval '1 hour'`, [email]);
  if ((recent?.n ?? 0) >= MAX_CODES_PER_HOUR) return { ok: false, error: "Too many codes requested. Wait an hour and try again." };
  const code = crypto.randomInt(0, 1_000_000).toString().padStart(6, "0");
  await q(`insert into login_codes (email, code_hash, expires_at) values ($1, $2, now() + make_interval(mins => $3))`, [email, hash(`${email}:${code}`), CODE_MINUTES]);
  await sendCode(email, code);
  return { ok: true };
}

async function sendCode(email: string, code: string) {
  const key = process.env.RESEND_API_KEY;
  if (!key) {
    if (process.env.NODE_ENV === "production") throw new Error("RESEND_API_KEY is not set.");
    console.log(`[dev] sign-in code for ${email}: ${code}`); // development only; never logged in production
    return;
  }
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: process.env.EMAIL_FROM, to: email, subject: `${code} is your Festora sign-in code`,
      text: `Your Festora sign-in code is ${code}.\n\nIt expires in ${CODE_MINUTES} minutes. If you did not ask for it, you can ignore this email.`,
    }),
  });
  if (!r.ok) throw new Error(`Email failed with status ${r.status}`);
}

export async function verifyCode(emailRaw: string, code: string): Promise<{ ok: true } | { ok: false; error: string }> {
  const email = normaliseEmail(emailRaw);
  const row = await one<{ id: string; code_hash: string; attempts: number }>(
    `select id, code_hash, attempts from login_codes where email = $1 and used_at is null and expires_at > now() order by created_at desc limit 1`, [email]);
  if (!row) return { ok: false, error: "That code has expired. Request a new one." };
  if (row.attempts >= MAX_ATTEMPTS) return { ok: false, error: "Too many wrong tries. Request a new code." };
  const good = crypto.timingSafeEqual(Buffer.from(row.code_hash), Buffer.from(hash(`${email}:${code.trim()}`)));
  if (!good) { await q(`update login_codes set attempts = attempts + 1 where id = $1`, [row.id]); return { ok: false, error: "That code is not right. Check the email and try again." }; }
  await q(`update login_codes set used_at = now() where id = $1`, [row.id]);
  const user = (await one<{ id: string }>(`insert into users (email) values ($1) on conflict (email) do update set email = excluded.email returning id`, [email]))!;
  const token = crypto.randomBytes(32).toString("base64url");
  await q(`insert into sessions (token_hash, user_id, expires_at) values ($1, $2, now() + make_interval(days => $3))`, [hash(token), user.id, SESSION_DAYS]);
  (await cookies()).set(COOKIE, token, { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", maxAge: SESSION_DAYS * 86400 });
  return { ok: true };
}

export async function currentUser(): Promise<User | null> {
  const token = (await cookies()).get(COOKIE)?.value;
  if (!token) return null;
  return one<User>(`select u.id, u.email, u.name, u.role from sessions s join users u on u.id = s.user_id where s.token_hash = $1 and s.expires_at > now()`, [hash(token)]);
}

export async function signOut(everywhere = false) {
  const jar = await cookies(); const token = jar.get(COOKIE)?.value;
  if (token) {
    if (everywhere) await q(`delete from sessions where user_id = (select user_id from sessions where token_hash = $1)`, [hash(token)]);
    else await q(`delete from sessions where token_hash = $1`, [hash(token)]);
  }
  jar.delete(COOKIE);
}

/** Deletes the account. Vendor profiles are unpublished and detached; past bookings keep only what the vendor needs. */
export async function deleteAccount(userId: string) {
  await q(`update services set status = 'draft' where vendor_id in (select id from vendors where owner_id = $1)`, [userId]);
  await q(`update equipment set status = 'draft' where vendor_id in (select id from vendors where owner_id = $1)`, [userId]);
  await q(`delete from users where id = $1`, [userId]); // sessions cascade; vendors.owner_id and bookings.customer_id become null
  (await cookies()).delete(COOKIE);
}
