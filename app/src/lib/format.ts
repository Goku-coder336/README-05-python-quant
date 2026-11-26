const LOCALE: Record<string, string> = { INR: "en-IN", AED: "en-AE", GBP: "en-GB", USD: "en-US" };

export function money(minor: number, currency: string) {
  return new Intl.NumberFormat(LOCALE[currency] ?? "en-IN", { style: "currency", currency, maximumFractionDigits: minor % 100 ? 2 : 0 }).format(minor / 100);
}

export function niceDate(iso: string) {
  return new Date(iso + "T00:00:00").toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", year: "numeric" });
}

export const unitLabel = { event: "per event", day: "per day", hour: "per hour", person: "per guest" } as const;
