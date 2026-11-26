# Architecture: all-in-one event services + equipment rental

Built from `replica/recon.md`, extended for the hybrid idea: one place to plan an event, book the people (planners, makeup, photographers, caterers) and rent the gear (sound, lighting, power, stage), organised by country, region and tradition.

## The core idea in the data

```
Country -> State -> City -> Area          (currency, tax, language, time zone)
Tradition (Kerala Hindu, Kerala Christian, Kerala Muslim, Tamil, Punjabi, Western...)
Event type (wedding, engagement, haldi, nikah, baptism, birthday, corporate, intimate dinner, proposal...)
Size tier (intimate <= 50, medium, large)
        |
        v
Event template = checklist of categories for that combination
        |
        v
Customer's Event (their planner) -> checklist -> shortlist -> enquiries -> bookings
        |
        v
Services (people, packages)  +  Equipment (rentable units with a calendar and deposit)
```

Tradition is used to **suggest and filter**, never to restrict. Anyone can book anything.

Example: "Kerala Christian wedding, Kochi, intimate (40 guests)" pre-fills a checklist: church decor, bridal makeup (Kerala Christian style), candid photographer, small-venue sound system plus technician, catering, cake, transport. The customer ticks, edits and books, all in one event page.

## Step 1: stack

| layer | choice | why |
| --- | --- | --- |
| web app | Next.js (App Router) + TypeScript | SEO pages per city/category, one codebase for web and API |
| styling | Tailwind + tokens from replica-design | fast, consistent |
| mobile | PWA first; Expo later | most users arrive from WhatsApp links |
| database | Postgres on Supabase | RLS, auth, storage, realtime in one managed service |
| ORM | Drizzle | typed SQL, works with range types |
| auth | Supabase Auth: phone OTP (India, UAE), email + Google (UK, US) | matches how each market signs in |
| payments | Razorpay (India), Stripe (everywhere else) behind one `payments` module | local cards/UPI; Stripe supports deposit holds |
| messaging | WhatsApp Business Cloud API (official) + email via Resend | vendors live on WhatsApp |
| jobs | Inngest | reminders, deposit release, payouts, hold expiry |
| files | Supabase Storage (or R2 later) | portfolios, handover photos |
| search | Postgres full text + trigram first; Meilisearch when > ~50k listings | no extra service at launch |
| i18n | next-intl; content tables carry `locale` | Malayalam, Tamil, Hindi, Arabic, English |
| hosting | Vercel | zero ops |

One database. No microservices.

## Step 2: schema

Full SQL in `replica/schema.sql`. 27 tables:

- **Places and culture:** countries, regions, traditions, event_types, categories, style_tags, event_templates, event_template_items
- **People:** profiles, vendors, vendor_traditions
- **Catalogue:** services, equipment, equipment_units, media
- **Customer planner:** events, event_checklist, shortlist
- **Transactions:** enquiries, bookings, booking_lines, unit_holds, vendor_blackouts, payments, handovers, reviews, webhook_events

Hard constraints:
- **No double-booked gear:** `unit_holds` has a GiST exclusion constraint on (unit, time range). Two customers cannot hold the same speaker for overlapping times, enforced by the database.
- **Money:** integer minor units + currency on every price. Each country has its own currency and tax rate.
- **Times:** `timestamptz` in UTC; each region stores its IANA time zone for display.
- **Webhook idempotency:** `payments (provider, provider_ref, kind)` unique, plus `webhook_events`.
- **Access:** Supabase row level security. Public reads live listings; vendors own their rows; customers own their events and bookings; payments written only by the server.

## Step 3: API (server actions and routes)

| flow | method path | does | who |
| --- | --- | --- | --- |
| Discover | GET `/[country]/[city]` | city home: event types, traditions, top vendors | public |
| | GET `/[country]/[city]/[category]` | listing with filters: style, tradition, guest size, price, date available | public |
| | GET `/v/[handle]` | vendor profile: services, equipment, reviews | public |
| | GET `/s/[id]`, `/e/[id]` | service package / equipment item with live availability | public |
| Plan | POST `createEvent` | event type + tradition + city + guests → copies template into checklist | customer |
| | GET `/my/events/[id]` | the event hub: checklist, shortlist, bookings, payments, timeline | owner |
| | POST `shortlistAdd`, `checklistUpdate` | | owner |
| Enquire | POST `createEnquiry` | message vendor; WhatsApp alert to vendor | customer |
| | POST `quoteEnquiry` | vendor sends price | vendor |
| Book | POST `createBooking` | service and/or equipment lines; places `unit_holds` for 15 min | customer |
| | POST `acceptBooking` | vendor confirms | vendor |
| | POST `checkout` | advance payment + deposit hold (Stripe manual capture / Razorpay authorisation or refundable deposit) | customer |
| | POST `handover` | out/in checklist with photos; damage flag | vendor |
| | POST `completeBooking` | releases deposit or opens dispute | system/vendor |
| Vendor | `/vendor/onboarding` | phone OTP → business → categories → traditions → areas → ID/licence | vendor |
| | `/vendor/dashboard` | enquiries, bookings, calendar, listings, payouts | vendor |
| Admin | `/admin` | verify vendors, manage templates and traditions per region, disputes | admin |
| Webhooks in | POST `/api/webhooks/stripe`, `/razorpay`, `/whatsapp` | payment status, inbound replies | providers |
| Jobs | expire unpaid holds (every 5 min), reminders (T-7d, T-1d), deposit auto-release (48h after return), review request (24h after event), payouts (daily) | | Inngest |

Official APIs only, with your own keys.

## Step 4: the parts that bite

- **Time zones:** events in Dubai, vendors in Kerala; always store UTC, display in the region's zone.
- **Double booking:** handled by the exclusion constraint; add setup/return buffers to every hold.
- **Deposits:** Stripe holds expire after about 7 days; for longer rentals charge a refundable deposit instead. Razorpay authorisations behave differently; test both.
- **Idempotency:** webhooks arrive twice; dedupe on provider event id.
- **Multi-country:** currency, tax (GST/VAT), language and payment provider come from `countries`, never hard-coded.
- **Cultural content:** traditions and templates are data, edited by admins with local vendors, not baked into code. Use respectful, community-checked wording.
- **Search:** filters on tradition, style, guest size, price and date availability; date availability is the expensive one, so query `unit_holds` and `vendor_blackouts` with indexes.
- **WhatsApp:** template messages need Meta approval; budget a week.
- **Privacy:** India DPDP, UK/EU GDPR: consent at signup, delete on request, hide phone numbers until a booking is accepted.
- **Disintermediation:** keep value inside: deposit protection, invoices, reviews, payment schedule.

## Step 5: build order

**M1: vertical slice (2–3 weeks)**
Kochi only. Vendor signs up (S09), lists one service and one equipment item; customer finds it (S04), books it (S05 → checkout), pays advance; vendor sees it in dashboard (S11).
Tables: countries, regions, categories, profiles, vendors, services, equipment, equipment_units, bookings, booking_lines, unit_holds, payments.

**M2: the event hub (2–3 weeks)**
Event types, traditions, templates, `createEvent`, checklist, shortlist, enquiries + quotes, WhatsApp alerts. Seed templates: Kerala Hindu / Christian / Muslim weddings, engagement, baptism, birthday, corporate, and **intimate** versions of each.

**M3: rental trust (2 weeks)**
Deposits, handover photos, damage flow, availability calendar, buffers, vendor blackouts, reviews.

**M4: discovery and SEO (1–2 weeks)**
City/category/tradition pages, filters (style, guest size, tradition, date), vendor verification badges, admin.

**M5: second city and second country**
Switch on Trivandrum and Calicut by data only. Then UAE: AED, VAT, Stripe, Arabic/English, Dubai regions, Gulf-specific templates.

**Later:** intimate-event concierge (one coordinator handles everything), invitation pages, group payments, mobile app, insurance partner, Meilisearch.

## Intimate events focus

- `size_tier = 'intimate'` on templates, events and service guest limits.
- Dedicated landing pages: "Intimate weddings in Kochi", "Small engagement setups", "Proposal setups", "Home baptism".
- Small packages: 2-hour photographer, compact sound kit, home decor, 20-person catering.
- Concierge option: one planner coordinates all vendors for a fixed fee.
