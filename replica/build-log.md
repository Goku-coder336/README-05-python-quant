# Build log

App: `app/` (Next.js 15.5, Tailwind, Beige and Brown tokens). Data layer is a JSON file (`app/.data/db.json`) behind `src/lib/data.ts`; replica-backend swaps in Postgres with the same functions.

| screen | date | status | missing / notes |
| --- | --- | --- | --- |
| Home `/` | 2026-11-26 | done | Serves landing v4 (two paths, multi-city waitlist). Waitlist form does not save yet. |
| Explore `/explore` | 2026-11-26 | done | Countries and cities from data; inactive countries show "coming later". |
| City `/[country]/[city]` | 2026-11-26 | done | Categories, intimate and tradition filters, empty state, local currency. No date or price filter yet. |
| Category `/[country]/[city]/[category]` | 2026-11-26 | done | Same view, filtered. |
| Vendor profile `/v/[handle]` | 2026-11-26 | done | No photos or reviews list yet. |
| Service `/s/[id]` | 2026-11-26 | partial | Request booking works and blocks a vendor's busy day. Photo gallery is a placeholder. |
| Equipment `/e/[id]` | 2026-11-26 | done | Date range, per-unit availability, deposit shown; overlapping booking blocked. |
| Booking sent `/bookings/[id]` | 2026-11-26 | done | Shows price, tax, deposit. No payment yet. |
| Vendor join `/vendor/join` | 2026-11-26 | done | Validation and errors. No phone OTP yet. |
| Vendor dashboard `/vendor/[handle]` | 2026-11-26 | partial | Owner-only (sign-in added). Accept or decline, add service or gear. No invoices yet. |
| Plan an event `/plan` | 2026-11-27 | done | Occasion, tradition, city, guests, date, budget; 50 guests or fewer gets the intimate checklist. |
| My events `/my/events` | 2026-11-27 | done | Progress bar per event; empty state. |
| Event page `/my/events/[id]` | 2026-11-27 | done | Checklist grouped by part of the day, budget and countdown, Find, shortlist, book, not needed, add and remove items, delete event. Owner-only. |
| Save to event (service and gear pages) | 2026-11-27 | done | Saves to the matching checklist item, or adds one. Bookings made from the plan tick the item off; a vendor decline puts it back to shortlisted. |

Harder than expected: nothing major. The "intimate" filter currently shows all rentals alongside small packages; gear needs its own guest-size field.
Verified: full journey in a browser at 390px and 1440px (vendor joins, lists gear, customer books, overlap blocked, vendor accepts), no console errors, no sideways scroll, skip link first in tab order, 404 page.
