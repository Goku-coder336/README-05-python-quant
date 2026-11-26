# Backend

App code: `app/`. Database: Postgres (Supabase in production, local Postgres 16 for development).

## What runs today
| Part | How | Status |
| --- | --- | --- |
| Database | `app/db/migrations/001_init.sql`, applied by `npm run db:migrate`; sample data by `npm run db:seed` | done |
| Double bookings | Refused by the database: exclusion constraints on gear units (`unit_holds`) and vendor days (`vendor_day_holds`). Tested with two simultaneous requests: one saved, one told to pick other dates. | done |
| Sign-in | Email + 6-digit code (10 min expiry, 5 tries, 5 codes per hour per email, per-IP limit). Codes and session tokens stored only as HMAC hashes. Session cookie: httpOnly, SameSite=Lax, Secure in production, 30 days. | done |
| Sign out | This device, or all devices | done |
| Account deletion | Deletes the user and sessions; their listings go offline; vendors keep the booking record they need | done |
| Authorisation | Checked in SQL in `src/lib/data.ts` on every vendor read and write (owner_id = signed-in user). A second user gets a 404 on someone else's dashboard. Supabase row level security is a later hardening step. | done |
| Waitlist | `POST /api/waitlist` (email, role, city), validated, rate limited, upsert per email and role | done |
| Input validation | zod on every server action and the waitlist route | done |
| Phone OTP (SMS) | Needs an SMS provider account (MSG91 or Twilio for India, Twilio for UAE). The sign-in module is ready for a second channel. | not started |
| Payments | Razorpay (India) and Stripe (UAE, UK) in test mode: advance on acceptance, deposit hold for rentals, webhooks. Needs your test keys. | not started |
| Booking emails | Vendor: new request, cancellation. Customer: request sent, accepted, declined. Saved to an outbox first, sent straight away, retried up to 5 times with growing waits (tested with a broken email key), never sent twice for the same event (tested with a double click). Retry job: `POST /api/jobs/notifications` with `CRON_SECRET`, run every 5 minutes by a scheduler. Admin overview shows sent, waiting and failed. | done |
| WhatsApp alerts | WhatsApp Business Cloud API; needs Meta business verification (allow 1 to 2 weeks, start early). The outbox already has a whatsapp channel. | not started |
| Photo uploads | Vendor portfolio (12) and per listing (10). Checked by file content not name, 8 MB limit, 6 per upload, rate limited. Every photo is re-encoded to WebP at most 1600 px and **all metadata including GPS location is removed**. Stored in Supabase Storage (public bucket on its own domain); local folder in development. Owner-only delete and cover. | done |

## What you need to create (Claude does not sign up or handle keys)
1. **Supabase project** (free tier is fine to start). Copy the Postgres connection string into `app/.env.local` as `DATABASE_URL`, set `DATABASE_SSL=true`, then run `npm run db:migrate` and `npm run db:seed`. Check daily backups are on in the dashboard.
2. **Resend account** with your domain verified. Put the key in `RESEND_API_KEY` and set `EMAIL_FROM`. Without it, production sign-in refuses to start rather than silently failing.
3. **Supabase Storage:** create a public bucket called `media`, then set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` (keep the service key secret).
4. `SESSION_SECRET`: run `openssl rand -hex 32`.
5. `CRON_SECRET` and a scheduler (Vercel Cron or Supabase cron) calling the retry job every 5 minutes.
6. Later: Razorpay and Stripe test keys, an SMS provider, and a Meta business account for WhatsApp.

Every variable is listed in `app/.env.example`. `.env*` files are git-ignored (checked with `git check-ignore`).

## Security checklist
- [x] secrets only in env vars, `.env*` git-ignored, nothing secret in client code
- [x] input validated on the server (zod) on every action and route
- [x] authorisation checked on every vendor read and write, tested with a second user
- [x] rate limits on code requests, code checks, bookings and waitlist (per-IP limiter is per server instance; move to a shared store before running several instances)
- [ ] webhooks verify signatures (no webhooks yet; required with payments)
- [x] uploads: content-sniffed type, size and count limits, re-encoded with metadata stripped, served from a separate bucket domain; local route rejects path tricks (tested)
- [x] no personal data in URLs or logs (dev-only code logging is disabled in production)
- [~] dependencies audited: fixed `sharp` and moved to `zod` 4. **Open:** a PostCSS advisory inside Next.js 15's build tooling; the fix is Next.js 16, a major upgrade to schedule. It affects CSS processing at build time, not visitor requests.
- [ ] privacy policy lists processors (Supabase, Resend, Razorpay, Stripe, Meta, host)
