import type { DB } from "./types";

// Sample data so every screen has something real to show. Vendors are fictional.
const now = "2026-11-20T09:00:00.000Z";

export const seed: DB = {
  countries: [
    { code: "IN", name: "India", currency: "INR", locale: "en-IN", taxName: "GST", taxRateBp: 1800, active: true },
    { code: "AE", name: "United Arab Emirates", currency: "AED", locale: "en-AE", taxName: "VAT", taxRateBp: 500, active: true },
    { code: "GB", name: "United Kingdom", currency: "GBP", locale: "en-GB", taxName: "VAT", taxRateBp: 2000, active: false },
  ],
  regions: [
    { id: "r-kl", countryCode: "IN", parentId: null, kind: "state", name: "Kerala", slug: "kerala", timezone: "Asia/Kolkata", active: true },
    { id: "r-ka", countryCode: "IN", parentId: null, kind: "state", name: "Karnataka", slug: "karnataka", timezone: "Asia/Kolkata", active: true },
    { id: "r-tn", countryCode: "IN", parentId: null, kind: "state", name: "Tamil Nadu", slug: "tamil-nadu", timezone: "Asia/Kolkata", active: true },
    { id: "r-dxb-e", countryCode: "AE", parentId: null, kind: "state", name: "Dubai", slug: "dubai-emirate", timezone: "Asia/Dubai", active: true },
    { id: "c-kochi", countryCode: "IN", parentId: "r-kl", kind: "city", name: "Kochi", slug: "kochi", timezone: "Asia/Kolkata", active: true },
    { id: "c-tvm", countryCode: "IN", parentId: "r-kl", kind: "city", name: "Trivandrum", slug: "trivandrum", timezone: "Asia/Kolkata", active: true },
    { id: "c-clt", countryCode: "IN", parentId: "r-kl", kind: "city", name: "Calicut", slug: "calicut", timezone: "Asia/Kolkata", active: true },
    { id: "c-tcr", countryCode: "IN", parentId: "r-kl", kind: "city", name: "Thrissur", slug: "thrissur", timezone: "Asia/Kolkata", active: true },
    { id: "c-blr", countryCode: "IN", parentId: "r-ka", kind: "city", name: "Bengaluru", slug: "bengaluru", timezone: "Asia/Kolkata", active: true },
    { id: "c-chn", countryCode: "IN", parentId: "r-tn", kind: "city", name: "Chennai", slug: "chennai", timezone: "Asia/Kolkata", active: true },
    { id: "c-dxb", countryCode: "AE", parentId: "r-dxb-e", kind: "city", name: "Dubai", slug: "dubai", timezone: "Asia/Dubai", active: true },
  ],
  traditions: [
    { id: "t-kh", slug: "kerala-hindu", name: "Kerala Hindu" },
    { id: "t-kc", slug: "kerala-christian", name: "Kerala Christian" },
    { id: "t-km", slug: "kerala-muslim", name: "Kerala Muslim" },
    { id: "t-ta", slug: "tamil", name: "Tamil" },
    { id: "t-any", slug: "any", name: "Any or mixed" },
  ],
  categories: [
    { id: "k-plan", slug: "event-planners", name: "Event planners", kind: "service", icon: "ClipboardText" },
    { id: "k-mua", slug: "makeup", name: "Makeup artists", kind: "service", icon: "PaintBrush" },
    { id: "k-photo", slug: "photography", name: "Photographers", kind: "service", icon: "Camera" },
    { id: "k-video", slug: "videography", name: "Videographers", kind: "service", icon: "VideoCamera" },
    { id: "k-decor", slug: "decor", name: "Decor", kind: "service", icon: "FlowerLotus" },
    { id: "k-cater", slug: "catering", name: "Catering", kind: "service", icon: "CookingPot" },
    { id: "k-sound", slug: "sound", name: "Sound rental", kind: "equipment", icon: "SpeakerHifi" },
    { id: "k-light", slug: "lighting", name: "Lighting rental", kind: "equipment", icon: "Lightbulb" },
    { id: "k-power", slug: "generators", name: "Generators", kind: "equipment", icon: "Lightning" },
  ],
  vendors: [
    { id: "v1", handle: "lumen-frames", businessName: "Lumen Frames", bio: "Candid wedding stories across central Kerala. Small teams, quiet presence.", baseRegionId: "c-kochi", servesRegionIds: ["c-kochi", "c-tcr"], phone: "+910000000001", verification: "verified", ratingAvg: 4.9, ratingCount: 38, traditionIds: ["t-kc", "t-kh"], createdAt: now },
    { id: "v2", handle: "kayal-sound", businessName: "Kayal Sound and Light", bio: "PA systems, stage lighting and generators with trained technicians.", baseRegionId: "c-kochi", servesRegionIds: ["c-kochi", "c-tcr", "c-tvm"], phone: "+910000000002", verification: "verified", ratingAvg: 4.7, ratingCount: 61, traditionIds: [], createdAt: now },
    { id: "v3", handle: "mira-studio", businessName: "Mira Bridal Studio", bio: "Bridal looks with kasavu and saree draping, plus family makeup.", baseRegionId: "c-tcr", servesRegionIds: ["c-tcr", "c-kochi"], phone: "+910000000003", verification: "verified", ratingAvg: 4.8, ratingCount: 54, traditionIds: ["t-kh", "t-kc"], createdAt: now },
    { id: "v4", handle: "nilavu-decor", businessName: "Nilavu Decor", bio: "Mandapam, church and nikah stage decor with fresh flowers.", baseRegionId: "c-kochi", servesRegionIds: ["c-kochi"], phone: "+910000000004", verification: "pending", ratingAvg: 0, ratingCount: 0, traditionIds: ["t-kh", "t-kc", "t-km"], createdAt: now },
    { id: "v5", handle: "desert-beats", businessName: "Desert Beats Events", bio: "Sound and lighting for weddings and community events in Dubai.", baseRegionId: "c-dxb", servesRegionIds: ["c-dxb"], phone: "+971000000005", verification: "verified", ratingAvg: 4.6, ratingCount: 22, traditionIds: [], createdAt: now },
  ],
  services: [
    { id: "s1", vendorId: "v1", categoryId: "k-photo", title: "Candid wedding story, 4 hours", description: "One lead photographer and an assistant. Edited gallery in three weeks.", included: ["300 edited photos", "Online gallery", "20 page album"], priceMinor: 3500000, currency: "INR", priceUnit: "event", minGuests: null, maxGuests: 80, advancePct: 30, styles: ["candid", "intimate"], traditionIds: ["t-kc", "t-kh"], status: "live" },
    { id: "s2", vendorId: "v1", categoryId: "k-photo", title: "Full day photo and film", description: "Two photographers and a filmmaker from getting ready to reception.", included: ["600 edited photos", "5 minute film", "Drone shots"], priceMinor: 12500000, currency: "INR", priceUnit: "event", minGuests: 50, maxGuests: null, advancePct: 30, styles: ["candid", "cinematic"], traditionIds: ["t-kc", "t-kh"], status: "live" },
    { id: "s3", vendorId: "v3", categoryId: "k-mua", title: "Bridal look with kasavu draping", description: "Trial session, wedding day look and draping. HD products.", included: ["Trial session", "Hair styling", "Saree draping"], priceMinor: 1800000, currency: "INR", priceUnit: "event", minGuests: null, maxGuests: null, advancePct: 25, styles: ["traditional"], traditionIds: ["t-kh"], status: "live" },
    { id: "s4", vendorId: "v4", categoryId: "k-decor", title: "Intimate home decor, up to 40 guests", description: "Floral backdrop, entrance and table styling for small gatherings.", included: ["Floral backdrop", "Entrance arch", "Table styling"], priceMinor: 4200000, currency: "INR", priceUnit: "event", minGuests: null, maxGuests: 40, advancePct: 40, styles: ["intimate", "minimal"], traditionIds: ["t-any"], status: "live" },
  ],
  equipment: [
    { id: "e1", vendorId: "v2", categoryId: "k-sound", title: "Compact PA kit for 80 guests", description: "Two speakers, mixer and two wireless microphones.", specs: { Power: "2 x 1000 W", Mics: "2 wireless" }, dayRateMinor: 450000, depositMinor: 500000, currency: "INR", needsOperator: true, units: 2, status: "live" },
    { id: "e2", vendorId: "v2", categoryId: "k-light", title: "Stage wash lights, set of 8", description: "Warm white LED wash with DMX controller.", specs: { Fixtures: "8 LED", Control: "DMX" }, dayRateMinor: 350000, depositMinor: 400000, currency: "INR", needsOperator: false, units: 1, status: "live" },
    { id: "e3", vendorId: "v2", categoryId: "k-power", title: "Silent generator 15 kVA", description: "Diesel, soundproof canopy. Delivery inside Kochi included.", specs: { Output: "15 kVA" }, dayRateMinor: 600000, depositMinor: 1000000, currency: "INR", needsOperator: false, units: 1, status: "live" },
    { id: "e4", vendorId: "v5", categoryId: "k-sound", title: "Wedding PA package", description: "Speakers, subwoofer and DJ console for up to 200 guests.", specs: { Guests: "Up to 200" }, dayRateMinor: 180000, depositMinor: 100000, currency: "AED", needsOperator: true, units: 1, status: "live" },
  ],
  bookings: [
    { id: "b-demo", vendorId: "v2", itemKind: "equipment", itemId: "e2", itemTitle: "Stage wash lights, set of 8", customerName: "Anu Joseph", customerPhone: "+910000000099", note: "Church hall, evening reception", startsOn: "2027-01-16", endsOn: "2027-01-16", unitIndex: 0, subtotalMinor: 350000, taxMinor: 63000, depositMinor: 400000, currency: "INR", status: "accepted", createdAt: now },
  ],
};
