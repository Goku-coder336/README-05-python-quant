// Mirrors replica/schema.sql. Money is integer minor units (paise, fils, pence) plus a currency.

export type Country = { code: string; name: string; currency: string; locale: string; taxName: string; taxRateBp: number; active: boolean };
export type Region = { id: string; countryCode: string; parentId: string | null; kind: "state" | "city"; name: string; slug: string; timezone: string; active: boolean };
export type Tradition = { id: string; slug: string; name: string };
export type Category = { id: string; slug: string; name: string; kind: "service" | "equipment"; icon: string };

export type Vendor = {
  id: string; handle: string; businessName: string; bio: string; baseRegionId: string; servesRegionIds: string[];
  phone: string; verification: "pending" | "verified"; ratingAvg: number; ratingCount: number; traditionIds: string[]; createdAt: string;
};

export type Service = {
  id: string; vendorId: string; categoryId: string; title: string; description: string; included: string[];
  priceMinor: number; currency: string; priceUnit: "event" | "day" | "hour" | "person";
  minGuests: number | null; maxGuests: number | null; advancePct: number; styles: string[]; traditionIds: string[]; status: "draft" | "live";
};

export type Equipment = {
  id: string; vendorId: string; categoryId: string; title: string; description: string; specs: Record<string, string>;
  dayRateMinor: number; depositMinor: number; currency: string; needsOperator: boolean; units: number; status: "draft" | "live";
};

export type BookingStatus = "requested" | "accepted" | "declined" | "cancelled" | "completed";
export type Booking = {
  id: string; vendorId: string; itemKind: "service" | "equipment"; itemId: string; itemTitle: string;
  customerName: string; customerPhone: string; note: string;
  startsOn: string; endsOn: string; // ISO dates, inclusive, in the region's time zone
  unitIndex: number | null; // which physical unit is held, for equipment
  subtotalMinor: number; taxMinor: number; depositMinor: number; currency: string;
  status: BookingStatus; createdAt: string;
};

export type DB = {
  countries: Country[]; regions: Region[]; traditions: Tradition[]; categories: Category[];
  vendors: Vendor[]; services: Service[]; equipment: Equipment[]; bookings: Booking[];
};
