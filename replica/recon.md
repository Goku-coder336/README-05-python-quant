# Recon map: EventKompany (web) mapped to a trade buyer directory

Recon date: 2026-11-25. Public pages only, read by hand. No login, no source code, no network logging.

## Scope

- **App:** EventKompany, web (eventkompany.com and vendor.eventkompany.com)
- **Slice:** core loop. Discover by location and category, view profile and package, enquire, vendor onboarding and dashboard
- **For:** a global directory of importers/buyers that helps exporters (and importers) find each other

## Sources

| source | URL | what it gave |
| --- | --- | --- |
| Home page | https://eventkompany.com | nav, location picker, categories, 3-step enquiry flow, spotlight vendors, footer |
| Category listing | https://eventkompany.com/services/wedding-photography | filters, sort, locked filters, empty state |
| Package page | https://eventkompany.com/package/bubble_artist-bubble-show | package layout, policies, cart, WhatsApp, gated reviews |
| Vendor onboarding | https://vendor.eventkompany.com/onboarding | step 1: WhatsApp number (+91) |
| Vendor portal meta | https://vendor.eventkompany.com | dashboard covers packages, orders, invoices |
| Play Store | https://play.google.com/store/apps/details?id=com.eventkompany.twa | Android app is a TWA (wrapped website) |

Not yet read: terms (check for any anti-competition clause before using an account), vendor register page, cart and checkout. Those need your own account.

## Screen inventory

| ID | screen | route | purpose | key components | states seen | trade equivalent |
| --- | --- | --- | --- | --- | --- | --- |
| S01 | Home | `/` | hero, find vendors, categories, spotlight | header, hero carousel, location input, city chips, stat strip, category grid, banners, 3-step explainer, vendor cards, vendor CTA, footer | filled | Home: search by product/HS code + country |
| S02 | Location modal | header "Select location" | set city/pincode | modal, text input, city chips | open | Country / region / port picker |
| S03 | Categories | `/services` | all categories | category grid | filled | HS chapter browser |
| S04 | Category listing | `/services/{slug}` | packages in a category | filter panel, budget slider, rating chips, sort, result count, cards | empty ("0 packages", "Stay tuned"), filters locked | Buyers for product X |
| S05 | Package detail | `/package/{vendor}-{slug}` | one offer | gallery + thumbs, price, vendor link, description, included list, availability (location, date), policies, WhatsApp link, Add to Cart | filled, reviews locked | Buying requirement detail |
| S06 | Vendor profile | `/@{handle}` | vendor page | (not read) | n/a | Buyer company profile |
| S07 | Cart | `/cart` | checkout, 50% advance | (not read) | n/a | Plan / paywall checkout |
| S08 | Sign in | "Account" | customer auth | (not read; likely phone OTP, a guess) | n/a | Member sign in |
| S09 | Vendor onboarding | vendor.../onboarding | start listing | step header, phone input with +91, Continue | step 1 | Buyer/supplier onboarding: company, role, country, HS codes, verification |
| S10 | Vendor register | vendor.../register | sign up | (not read) | n/a | same as S09 |
| S11 | Vendor dashboard | vendor... | manage packages, orders, invoices | (not read) | n/a | Requirements, enquiries, leads, plan |
| S12 | Static pages | `/about` `/terms` `/privacy` `/grievance-redressal` `/contact` `/blogs` | legal and content | text | n/a | same + GDPR pages, trade guides |

## User flows

```
F01 Customer finds and enquires a vendor   (trade: exporter finds a buyer)
    S01 -> S02 set location -> S04 category -> S05 package -> WhatsApp / quick enquiry
    happy path: about 5 clicks
    edge: 0 results in category (seen), filters locked until sign-in (seen), vendor outside base location (travel charges)

F02 Customer books a package   (trade: replaced by paying for a plan)
    S05 -> Add to Cart -> S07 -> S08 sign in -> pay 50% advance
    edge: cancellation inside 4 days (no refund), balance paid to vendor directly

F03 Vendor joins   (trade: buyer or supplier joins)
    S01 "Register as a vendor" -> S10/S09 WhatsApp number -> (further steps not seen) -> S11
    edge: non-Indian number (+91 fixed; your version must be international)

F04 Vendor manages listings   (trade: buyer posts a requirement / RFQ)
    S11 -> create package -> appears on S04/S05
```

The number to beat: 5 clicks from home to a contact.

## Components

| component | variants / states | used on |
| --- | --- | --- |
| Header nav | logo, Home, Categories, Account, Cart, location button | all |
| Location picker | modal, input, popular chips | S01, S02 |
| Category tile | image + label | S01, S03 |
| Listing card | image, title, price, rating | S04 |
| Vendor card | photo, name, category tags (+N), View profile | S01 |
| Filter panel | locked (sign-in overlay), unlocked; range slider; rating chips; sort radio | S04 |
| Empty state | icon + message | S04 |
| Gallery | main image, prev/next, thumbnails | S05 |
| Policy block | heading + bullet list | S05 |
| CTA buttons | primary (Add to Cart, Browse), secondary (Go to Cart), WhatsApp link | S01, S05 |
| Phone input | country code prefix, Continue | S09 |
| Stat strip | number + label | S01 |
| Footer | link columns, socials, app badge | all |

## Inferred data model

```
Vendor     id, handle, name, profile_pic, categories[], base_location, verified, rating
           evidence: spotlight cards (S01), @handle link (S05)   confidence: high
           -> trade: Company (buyer | supplier), country, HS codes, verification level, activity score

Category   id, slug, name, image          evidence: S01 grid, /services/{slug}   confidence: high
           -> trade: HS chapter/heading tree

Package    id, vendor_id, category_id, slug, title, price, description, included[], images[],
           cancellation_policy, payment_policy (advance %)
           evidence: S05   confidence: high
           -> trade: Requirement (product, spec, qty, unit, frequency, MOQ, Incoterms, destination port, payment terms)

Location   city, pincode (5000+)          evidence: S01/S02   confidence: high
           -> trade: country, region, port (UN/LOCODE)

Customer   id, phone, name                evidence: sign-in gates   confidence: medium (guess: phone OTP)
           -> trade: Member (exporter/importer) with plan

Order      id, customer_id, package_id, event_date, location, advance_paid, status
           evidence: cart, payment policy, vendor portal "orders, invoices"   confidence: medium
           -> trade: Subscription + Enquiry (from, to, requirement_id, message, status)

Review     id, package_id, customer_id, rating, text   evidence: "Login to view Ratings & Reviews"   confidence: medium
           -> trade: Deal review after a completed trade
```

## What cannot be cloned (skip)

- Their vendor network, photos, descriptions and reviews. These belong to EventKompany and its vendors.
- Their brand, logo, banners and copy.
- Licensed customs or import data. You need your own licence (Volza, Panjiva, ImportGenius, UN Comtrade for aggregates).
- Buyer contact data scraped from other directories (GDPR / DPDP risk). Build an opted-in buyer base.

## Size

- 12 screens, 4 flows, 6 core entities.
- Hard parts: (1) getting real, verified buyer data (not a code problem), (2) HS-code search with multilingual product names, (3) verification and anti-fraud, (4) international phone/email auth and payments in many currencies.
- Size: **M** (a few weeks) for the directory, RFQ and messaging MVP. Customs data integration and trade tools push it towards L.
