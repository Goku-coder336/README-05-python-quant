# Components: Festora (working name)

Base: shadcn/ui on Radix (accessible primitives), Lucide icons (ISC licence). Fonts: Fraunces (headings) and Inter (body), both open licence; Noto Sans Malayalam / Tamil / Arabic for local scripts. All colours via tokens. Mobile-first: designed at 360px, then widened.

Screen IDs refer to `replica/recon.md` (S01–S12) plus new hub screens: H01 event hub, H02 checklist, H03 equipment detail, H04 handover.

```
Header
  variants  default, transparent-over-hero
  parts     logo, city button, search, Account, Saved
  mobile    logo + city + search icon; nav moves to bottom bar
  a11y      <header>, skip link to main, city button opens dialog
  used on   all

Bottom nav (mobile)
  items     Explore, My event, Saved, Messages, Account
  states    active (accent icon + label), inactive (muted)
  a11y      <nav aria-label="Main">, aria-current="page"
  used on   all (< 768px)

City and region picker
  variants  dialog (mobile full-screen sheet), popover (desktop)
  parts     country tabs (IN, AE, GB...), search, popular cities, "use my location"
  states    loading, empty search, city not yet open ("Join the waitlist")
  a11y      Radix Dialog, focus trap, Esc closes, list is a listbox
  used on   S01, S02

Event starter ("Plan my event")
  parts     event type chips, tradition select, guest count stepper, date, city
  states    default, partially filled, submitting, error
  note      guest count <= 50 shows the "Intimate" badge and small packages first
  a11y      labelled fields, errors linked via aria-describedby
  used on   S01, H01

Button
  variants  primary (accent), secondary (outline), ghost, highlight (marigold, for offers), whatsapp, danger
  sizes     sm 36px, md 44px, lg 52px (44px minimum touch target)
  states    default, hover, active, focus-visible (2px focus ring), disabled, loading (spinner, label kept)
  tokens    primary: bg accent, text on-accent, radius pill, font sm/600
  a11y      real <button>; links styled as buttons stay <a>
  used on   everywhere

Input, Select, Textarea, Date picker, Phone input
  states    default, focus, filled, error (danger text + icon), disabled
  tokens    border border-input, radius md, height 44px
  phone     country code select (+91, +971, +44...), numeric keyboard
  a11y      visible <label>, error in aria-describedby, date picker keyboard-operable
  used on   S05, S09, H01

Chip / filter pill
  variants  choice (single), filter (multi), removable
  states    off, on (accent-soft bg, on-accent-soft text), focus, disabled
  used on   S01, S04 (style: candid, cinematic, traditional, drone; tradition; intimate)

Filter sheet
  parts     price range, date availability, guest size, style, tradition, rating, sort
  mobile    bottom sheet with "Show N results"; desktop: left sidebar
  states    locked (sign-in prompt) is NOT used: filters are open to everyone
  a11y      Dialog on mobile, fieldsets with legends
  used on   S04

Category tile
  parts     own photo or illustration, label
  variants  service, equipment (small gear badge)
  used on   S01, S03

Listing card (service)
  parts     cover image, vendor name, title, price "from", rating, style tags, "Intimate" badge, save heart
  states    default, hover (shadow pop), saved, unavailable on chosen date (muted + note)
  used on   S04, S06, H01

Listing card (equipment)
  parts     image, title, day rate, deposit, "with operator" badge, availability dot
  states    available, few left, unavailable on dates
  used on   S04, S06, H03

Vendor card
  parts     avatar, business name, categories, verified badge, rating, city
  used on   S01, S04

Badge
  variants  verified (success), intimate (accent-soft), offer (highlight), new, tradition
  used on   cards, profiles

Gallery
  parts     main image, swipe on mobile, thumbnails on desktop, video support
  a11y      prev/next buttons labelled, alt text required on upload
  used on   S05, S06, H03

Price and policy block
  parts     price, advance %, deposit (held, refundable), cancellation, what is included
  used on   S05, H03

Availability calendar
  parts     month grid, unavailable days struck through, selected range
  states    loading, no availability this month, range invalid
  a11y      grid role, arrow-key navigation, announced selection
  used on   H03, vendor dashboard

Booking summary (sticky)
  parts     selected lines (services + gear), dates, subtotal, tax, fee, deposit held, total, CTA
  mobile    sticky bottom bar that expands to a sheet
  used on   S05, H03, S07

Checklist row
  parts     category, sub-event (Haldi, Reception), status pill (to do, shortlisted, booked, skipped), "Find" button
  states    each status; booked shows the vendor
  used on   H01, H02

Event hub header
  parts     event title, date countdown, city, guest count, tradition, budget bar
  used on   H01

Budget bar
  parts     spent / budget, segments by category
  a11y      text values beside the bar, not colour only
  used on   H01

Message thread
  parts     bubbles, quote card (price, valid until, Accept), attachments
  states    sending, failed (retry), read
  used on   enquiries, vendor dashboard

WhatsApp button
  variant   button whatsapp; opens wa.me with a prefilled message
  used on   S05, S06

Handover checklist
  parts     item list, photo slots (front, back, serial), notes, damage toggle, sign-off
  states    out, in, damage reported
  used on   H04

Stepper (onboarding)
  parts     step count, title, progress bar
  used on   S09

Empty state
  parts     illustration (own), one line, action
  copy      "No photographers free on 14 Feb in Kochi yet. Try nearby dates or Thrissur."
  used on   S04, H01, dashboards

Toast
  variants  success, error, info
  a11y      role="status" (polite), errors role="alert"

Modal / sheet
  a11y      Radix Dialog, focus trap, Esc, returns focus

Skeleton
  used for  cards, gallery, calendar while loading

Footer
  parts     link columns, country/language switcher, socials, app badge later
```

## Layout

- Max width 1200px; 16px side gutter on mobile, 24px from 768px.
- Grid: 1 column under 640px, 2 at 640px, 3 at 1024px, 4 at 1280px for cards.
- Header 64px; mobile bottom nav 64px with safe-area padding.
- Right-to-left support for Arabic via `dir="rtl"` and logical CSS properties (`ms-`, `me-`).

## Visual direction

- Warm ivory background, deep plum accent (premium, works for every tradition), marigold for offers and highlights (festive without being loud).
- Fraunces headings give a wedding-invitation feel; Inter keeps forms and prices clear.
- Photography does the colour work; the interface stays calm.
- All imagery is our own or properly licensed; nothing from EventKompany.
