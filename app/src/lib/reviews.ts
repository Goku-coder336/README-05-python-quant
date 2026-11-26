import { one, pool, q } from "./db";

export type Review = { id: string; bookingId: string; authorName: string; rating: number; body: string; vendorReply: string | null;
  repliedAt: string | null; createdAt: string; itemTitle: string; hidden: boolean };
const COLS = `r.id, r.booking_id as "bookingId", r.author_name as "authorName", r.rating, r.body, r.vendor_reply as "vendorReply",
  r.replied_at as "repliedAt", r.created_at as "createdAt", b.item_title as "itemTitle", r.hidden`;

/** Public reviews for a vendor, newest first. Hidden ones are left out. */
export const vendorReviews = (vendorId: string, includeHidden = false) =>
  q<Review>(`select ${COLS} from reviews r join bookings b on b.id = r.booking_id where r.vendor_id = $1 and ($2 or not r.hidden) order by r.created_at desc`, [vendorId, includeHidden]);

/** Reviews for one listing (service or gear). */
export const listingReviews = (itemId: string) =>
  q<Review>(`select ${COLS} from reviews r join bookings b on b.id = r.booking_id where b.item_id = $1 and not r.hidden order by r.created_at desc limit 20`, [itemId]);

/** Bookings this customer may review: confirmed, event date passed, not yet reviewed. */
export const reviewable = (userId: string) => q<{ bookingId: string }>(`select b.id as "bookingId" from bookings b
  left join reviews r on r.booking_id = b.id
  where b.customer_id = $1 and b.status in ('accepted','completed') and b.ends_on < current_date and r.id is null`, [userId]);

export const myReviews = (userId: string) => q<Review>(`select ${COLS} from reviews r join bookings b on b.id = r.booking_id where r.customer_id = $1`, [userId]);

const publicName = (full: string) => {
  const parts = full.trim().split(/\s+/);
  return parts.length > 1 ? `${parts[0]} ${parts[parts.length - 1][0]}.` : parts[0];
};

export async function createReview(userId: string, bookingId: string, rating: number, body: string) {
  // All rules checked in one statement, so a crafted request cannot review someone else's or an unfinished booking.
  const r = await one<{ id: string }>(`insert into reviews (booking_id, vendor_id, customer_id, author_name, rating, body)
    select b.id, b.vendor_id, b.customer_id, $4, $3, $5 from bookings b
    where b.id = $1 and b.customer_id = $2 and b.status in ('accepted','completed') and b.ends_on < current_date
    on conflict (booking_id) do nothing returning id`, [bookingId, userId, rating, "", body]);
  if (!r) return null;
  const name = (await one<{ name: string }>(`select customer_name as name from bookings where id = $1`, [bookingId]))!.name;
  await pool.query(`update reviews set author_name = $2 where id = $1`, [r.id, publicName(name)]);
  return r;
}

/** Vendor's public reply; only the vendor's owner. Replacing an earlier reply is allowed. */
export async function replyToReview(userId: string, reviewId: string, reply: string) {
  const r = await pool.query(`update reviews r set vendor_reply = $3, replied_at = now() from vendors v
    where r.id = $1 and v.id = r.vendor_id and v.owner_id = $2`, [reviewId, userId, reply || null]);
  return (r.rowCount ?? 0) > 0;
}

export async function setHidden(reviewId: string, hidden: boolean, reason: string) {
  await pool.query(`update reviews set hidden = $2, hidden_reason = $3, updated_at = now() where id = $1`, [reviewId, hidden, hidden ? reason : null]);
}
export const latestReviews = () => q<Review & { vendorName: string; hiddenReason: string | null }>(`select ${COLS}, v.business_name as "vendorName", r.hidden_reason as "hiddenReason"
  from reviews r join bookings b on b.id = r.booking_id join vendors v on v.id = r.vendor_id order by r.created_at desc limit 50`);
