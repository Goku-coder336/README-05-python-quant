import { one, pool, q } from "./db";
import { sendEmail } from "./email";
import { money, niceDate } from "./format";

// Booking notifications. Each message is saved to the outbox, then sent. Failed sends are retried
// with backoff by processOutbox(), run after each event and by the /api/jobs/notifications route.

const APP = () => process.env.APP_URL ?? "http://localhost:3000";
type Kind = "booking.requested.vendor" | "booking.requested.customer" | "booking.accepted" | "booking.declined" | "booking.cancelled.vendor";

type Ctx = { id: string; itemTitle: string; startsOn: string; endsOn: string; subtotalMinor: number; depositMinor: number; currency: string;
  customerName: string; note: string; vendorName: string; vendorHandle: string; vendorPhone: string; vendorEmail: string | null; customerEmail: string | null };

async function ctx(bookingId: string) {
  return one<Ctx>(`select b.id, b.item_title as "itemTitle", b.starts_on as "startsOn", b.ends_on as "endsOn", b.subtotal_minor as "subtotalMinor",
      b.deposit_minor as "depositMinor", b.currency, b.customer_name as "customerName", b.note, v.business_name as "vendorName", v.handle as "vendorHandle",
      v.phone as "vendorPhone", vo.email as "vendorEmail", cu.email as "customerEmail"
    from bookings b join vendors v on v.id = b.vendor_id left join users vo on vo.id = v.owner_id left join users cu on cu.id = b.customer_id where b.id = $1`, [bookingId]);
}

const when = (c: Ctx) => c.startsOn === c.endsOn ? niceDate(c.startsOn) : `${niceDate(c.startsOn)} to ${niceDate(c.endsOn)}`;

function compose(kind: Kind, c: Ctx): { to: string | null; subject: string; body: string } {
  const sign = "\n\nUtsella";
  switch (kind) {
    case "booking.requested.vendor": return { to: c.vendorEmail, subject: `New request: ${c.itemTitle} on ${when(c)}`,
      body: `${c.customerName} would like to book ${c.itemTitle} for ${when(c)}.\n\nPrice: ${money(c.subtotalMinor, c.currency)}${c.depositMinor ? `, deposit ${money(c.depositMinor, c.currency)}` : ""}${c.note ? `\nTheir note: "${c.note}"` : ""}\n\nAccept or decline here: ${APP()}/vendor/${c.vendorHandle}\nCustomers hear back faster from vendors who reply within a few hours.${sign}` };
    case "booking.requested.customer": return { to: c.customerEmail, subject: `Request sent to ${c.vendorName}`,
      body: `We sent your request for ${c.itemTitle} on ${when(c)} to ${c.vendorName}. We will email you when they reply.\n\nSee all your bookings: ${APP()}/my/bookings${sign}` };
    case "booking.accepted": return { to: c.customerEmail, subject: `${c.vendorName} confirmed ${when(c)}`,
      body: `Good news. ${c.vendorName} accepted your booking for ${c.itemTitle} on ${when(c)}.\n\nYou can now message them on WhatsApp: https://wa.me/${c.vendorPhone.replace("+", "")}\nBooking details: ${APP()}/bookings/${c.id}${sign}` };
    case "booking.declined": return { to: c.customerEmail, subject: `${c.vendorName} cannot take ${when(c)}`,
      body: `${c.vendorName} is not able to take your booking for ${c.itemTitle} on ${when(c)}. Nothing was charged.\n\nFind another option in your area: ${APP()}/my/bookings${sign}` };
    case "booking.cancelled.vendor": return { to: c.vendorEmail, subject: `Cancelled: ${c.itemTitle} on ${when(c)}`,
      body: `${c.customerName} cancelled their booking for ${c.itemTitle} on ${when(c)}. The date is free again in your calendar.\n\nDashboard: ${APP()}/vendor/${c.vendorHandle}${sign}` };
  }
}

/** Queues the messages for a booking event. Safe to call twice: the unique index skips duplicates. */
export async function notifyBooking(bookingId: string, kinds: Kind[]) {
  const c = await ctx(bookingId); if (!c) return;
  for (const k of kinds) {
    const m = compose(k, c); if (!m.to) continue; // no account email (e.g. vendor without owner yet)
    await pool.query(`insert into notifications (to_address, subject, body, kind, booking_id) values ($1,$2,$3,$4,$5) on conflict do nothing`, [m.to, m.subject, m.body, k, bookingId]);
  }
  void processOutbox().catch(() => {}); // send now without making the user wait; retries pick up anything left
}

const MAX_ATTEMPTS = 5;
/** Sends due messages. Claims rows with SKIP LOCKED so two runners never send the same message. */
export async function processOutbox(limit = 20) {
  let sent = 0, failed = 0;
  for (let i = 0; i < limit; i++) {
    const c = await pool.connect();
    try {
      await c.query("begin");
      const row = (await c.query(`select id, to_address, subject, body, attempts from notifications
        where status = 'pending' and next_try_at <= now() order by id limit 1 for update skip locked`)).rows[0] as { id: number; to_address: string; subject: string; body: string; attempts: number } | undefined;
      if (!row) { await c.query("commit"); break; }
      try {
        await sendEmail(row.to_address, row.subject, row.body);
        await c.query(`update notifications set status = 'sent', sent_at = now(), attempts = attempts + 1 where id = $1`, [row.id]); sent++;
      } catch (e) {
        const n = row.attempts + 1;
        await c.query(`update notifications set attempts = $2, last_error = $3, status = case when $2 >= ${MAX_ATTEMPTS} then 'failed' else 'pending' end,
          next_try_at = now() + make_interval(mins => power(2, $2)::int) where id = $1`, [row.id, n, String((e as Error).message).slice(0, 300)]); failed++;
      }
      await c.query("commit");
    } catch (e) { await c.query("rollback"); throw e; } finally { c.release(); }
  }
  return { sent, failed };
}

/** Tells the vendor a new review arrived. Uses the outbox like booking messages. */
export async function notifyReview(reviewId: string) {
  const r = await one<{ to: string | null; handle: string; rating: number; item: string; author: string; booking: string }>(`select u.email as to, v.handle, rv.rating, b.item_title as item, rv.author_name as author, b.id as booking
    from reviews rv join vendors v on v.id = rv.vendor_id join bookings b on b.id = rv.booking_id left join users u on u.id = v.owner_id where rv.id = $1`, [reviewId]);
  if (!r?.to) return;
  await pool.query(`insert into notifications (to_address, subject, body, kind, booking_id) values ($1,$2,$3,'review.new',$4) on conflict do nothing`,
    [r.to, `New ${r.rating}-star review from ${r.author}`, `${r.author} reviewed ${r.item} (${r.rating} of 5 stars).\n\nRead it and reply publicly from your dashboard: ${APP()}/vendor/${r.handle}\n\nUtsella`, r.booking]);
  void processOutbox().catch(() => {});
}

export const outboxStats = () => q<{ status: string; n: number }>(`select status, count(*)::int as n from notifications group by status`);
