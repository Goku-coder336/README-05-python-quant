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
| Admin `/admin` | 2026-11-27 | done | Overview, waitlist demand by city, recent admin actions. Admin-only (others get 404). Make an admin with `npm run make-admin -- email`. |
| Admin vendors `/admin/vendors` | 2026-11-27 | done | Review list, verify or remove badge with a private note; every action logged. |
| Admin waitlist `/admin/waitlist` | 2026-11-27 | done | By city and role, latest sign-ups, CSV download with spreadsheet formula injection blocked. |
| Admin checklists `/admin/templates` | 2026-11-27 | done | Edit, add and delete checklist items per tradition; budget share total shown. New plans use the changes. |
| Photos (dashboard, cards, galleries, portfolio) | 2026-11-27 | done | Upload, delete, set cover; cover on cards; gallery on listing pages; portfolio on profiles. Test caught the photo section collapsing after upload; fixed. No alt text editing yet. |
| Booking emails | 2026-11-27 | done | Five messages, outbox with retries and de-duplication. Customers now sign in before requesting, so replies can reach them. |
| My bookings `/my/bookings` | 2026-11-27 | done | Upcoming and past, WhatsApp the vendor once confirmed, withdraw or cancel (frees the date and the plan item). Booking pages now visible only to the customer, the vendor and admins. |
| Any kind of event | 2026-11-27 | done | 34 occasions in 6 groups (family, religious and cultural, parties, business, community, something else), each with a starter checklist; 16 new vendor categories (venues, priests, AV and LED, stages, tents, security, cleaning, live streaming…); 6 more traditions. Plan form picks a group then an occasion. |
| Admin catalogue `/admin/catalogue` | 2026-11-27 | done | Create occasions (auto starter checklist), vendor categories and traditions; hide or show any of them. New checklist per occasion, tradition and size, optionally copied. Note: one React hydration warning seen once in development on /in/kochi right after adding a category; not reproduced in 7 further loads. Recheck on the production build. |
| Legal pages `/legal/terms`, `/legal/privacy`, `/legal/refunds`, `/contact` | 2026-11-27 | draft | Written for an intermediary marketplace (India first, UK and UAE in mind). Linked from app and landing footers. Business facts left as highlighted placeholders; a visible "draft for legal review" notice stays until a lawyer approves. |
| Rename to Utsella | 2026-11-27 | done | Name, logo, page titles, emails, legal pages, session cookie (`utsella_session`), CSV file name. Scanner clean for the app; old landing drafts v1 to v3 still say Festora (not shipped). Local database renamed to match. |
| Reviews and ratings | 2026-11-27 | done | One review per real booking, only after the event date, only by that customer (enforced in the database; tested a stranger's attempt: 0 rows). Public name is first name and last initial. Vendor average kept in step by a database trigger (seeded fake ratings reset to 0). Vendor public replies; vendor emailed on new review. Admin can hide with a reason (stops counting) and show again. Reviews on vendor profiles and listing pages. Test caught the thank-you message vanishing because Next.js refreshes the current page on any revalidation inside an action; fixed. Not yet: reminder email asking customers to review after the event. |
