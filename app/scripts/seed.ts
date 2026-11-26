// Loads the fictional sample data. Safe to re-run: skips rows that exist. Usage: npm run db:seed
import pg from "pg";
import { seed } from "../src/lib/seed.ts";
const c = new pg.Client({ connectionString: process.env.DATABASE_URL }); await c.connect();
const q = (sql: string, v: unknown[]) => c.query(sql + " on conflict do nothing", v);
for (const x of seed.countries) await q("insert into countries values ($1,$2,$3,$4,$5,$6,$7)", [x.code, x.name, x.currency, x.locale, x.taxName, x.taxRateBp, x.active]);
for (const x of [...seed.regions].sort((a, b) => Number(!!a.parentId) - Number(!!b.parentId))) await q("insert into regions values ($1,$2,$3,$4,$5,$6,$7,$8)", [x.id, x.countryCode, x.parentId, x.kind, x.name, x.slug, x.timezone, x.active]);
for (const x of seed.traditions) await q("insert into traditions values ($1,$2,$3)", [x.id, x.slug, x.name]);
for (const x of seed.categories) await q("insert into categories values ($1,$2,$3,$4,$5)", [x.id, x.slug, x.name, x.kind, x.icon]);
for (const x of seed.vendors) await q("insert into vendors (id,handle,business_name,bio,base_region_id,serves_region_ids,phone,verification,rating_avg,rating_count,tradition_ids) values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)", [x.id, x.handle, x.businessName, x.bio, x.baseRegionId, x.servesRegionIds, x.phone, x.verification, x.ratingAvg, x.ratingCount, x.traditionIds]);
for (const x of seed.services) await q("insert into services (id,vendor_id,category_id,title,description,included,price_minor,currency,price_unit,min_guests,max_guests,advance_pct,styles,tradition_ids,status) values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)", [x.id, x.vendorId, x.categoryId, x.title, x.description, x.included, x.priceMinor, x.currency, x.priceUnit, x.minGuests, x.maxGuests, x.advancePct, x.styles, x.traditionIds, x.status]);
for (const x of seed.equipment) await q("insert into equipment (id,vendor_id,category_id,title,description,specs,day_rate_minor,deposit_minor,currency,needs_operator,units,status) values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)", [x.id, x.vendorId, x.categoryId, x.title, x.description, x.specs, x.dayRateMinor, x.depositMinor, x.currency, x.needsOperator, x.units, x.status]);
for (const b of seed.bookings) {
  await q("insert into bookings (id,vendor_id,item_kind,item_id,item_title,customer_name,customer_phone,note,starts_on,ends_on,unit_index,subtotal_minor,tax_minor,deposit_minor,currency,status) values ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16)", [b.id, b.vendorId, b.itemKind, b.itemId, b.itemTitle, b.customerName, b.customerPhone, b.note, b.startsOn, b.endsOn, b.unitIndex, b.subtotalMinor, b.taxMinor, b.depositMinor, b.currency, b.status]);
  if (b.itemKind === "equipment") await q("insert into unit_holds values ($1,$2,$3,daterange($4::date,$5::date,'[]'))", [b.id, b.itemId, b.unitIndex, b.startsOn, b.endsOn]);
}
console.log("seeded"); await c.end();
