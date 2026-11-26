# Utsella: handover note

Read this first when continuing in a new session. Last updated 27 November 2026.

## What Utsella is
An all-in-one marketplace for **any kind of event** (weddings, pujas, conferences, birthdays, launches and 34 occasions in all): customers plan an event with a checklist shaped by occasion, tradition and guest count, then find and book **service vendors** (planners, makeup, photographers, caterers) and **rent professional gear** (sound, lights, generators, stages) in one place. Two paths: customers and vendors. Kerala first, then South India, UAE, UK. Formerly working name "Festora", renamed because a UK events company uses it.

## Where everything is (branch `claude/eventkompany-buyer-marketplace-4jailw`)
| Path | What |
| --- | --- |
| `app/` | The Next.js 15 app (TypeScript, Tailwind, Postgres). |
| `app/db/migrations/001-007` | Database schema. `npm run db:migrate`, `npm run db:seed`, `npm run make-admin -- email`. |
| `app/.env.example` | Every setting the app needs (no values). |
| `app/public/landing.html` | Landing page served at `/` (copy of `replica/landing/v4.html`). |
| `replica/architecture.md` | Stack, data model, routes, risks. |
| `replica/backend.md` | Backend checklist and what the owner must set up. |
| `replica/build-log.md` | Every screen built, with status and known gaps. |
| `replica/brand.md` | Name screening; Utsella checks still to run. |
| `replica/design/tokens.json` | Beige and Brown palette (passes contrast checks). |
| `replica/features.csv` | Feature matrix. |
| `.claude/skills/replica-*` | The Replica skill pack used to plan and build. |

## Built and tested
Landing page (customer and vendor paths, multi-city waitlist saved to the database) · cities and categories by country with local currency and tax · vendor profiles, service and gear pages with photo galleries · booking requests with database-enforced double-booking protection · email-code sign-in, sign out everywhere, account deletion · event planner for 34 occasions with tradition checklists, shortlist, budget, bookings ticking items off · My bookings with cancel and WhatsApp once confirmed · booking emails through an outbox with retries · photo uploads (re-encoded, GPS removed) · verified-booking reviews with vendor replies and moderation · admin: overview, vendor verification, waitlist by city with CSV, checklist editor, event types, categories and traditions, reviews · draft legal pages (terms, privacy, refunds, contact) with placeholders.

## Not built yet
Online payments (Razorpay Route in India, Stripe Connect abroad) · review reminder email · vendor availability calendars · WhatsApp alerts (needs Meta approval) · phone OTP (needs SMS provider) · deployment (Supabase, Vercel, Resend, cron for the email retry job) · Next.js 16 upgrade for a build-tool security advisory.

## Waiting on the owner
1. Utsella name checks: UK and India trademarks (classes 35, 41, 42), WIPO, MCA, domains, social handles; ideally a trademark attorney.
2. Domain purchase.
3. Accounts: Supabase (Mumbai region, public bucket `media`), Resend (verified sending subdomain), Vercel, Razorpay test key. Keys go into Vercel environment settings or a secure form, never into chat or git.
4. Business decisions for the refund page: commission, advance %, cancellation days and percentages, deposit release days, refund days, record retention.
5. Legal placeholders (business name, address, contacts, grievance officer), then a lawyer's review.
6. Business setup before taking money: Udyam, Shop and Establishment, current account; GST registration before online payments (e-commerce operator rules; confirm with a CA). If living abroad on a visa, check visa and residency rules before trading.

## Plan to continue
1. Stage 1 launch without payments (requests only): deploy with Supabase, Vercel, Resend.
2. Fill legal pages with the owner's details.
3. Payments once the Razorpay key and business setup are ready.
4. Then review reminders, availability calendars, WhatsApp alerts.

## Running it locally
```bash
cd app && cp .env.example .env.local   # fill DATABASE_URL and SESSION_SECRET at least
npm install && npm run db:migrate && npm run db:seed
npm run dev                            # http://localhost:3000; sign-in codes print in the terminal without RESEND_API_KEY
```
