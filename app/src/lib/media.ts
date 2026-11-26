import crypto from "node:crypto";
import sharp from "sharp";
import { one, pool, q } from "./db";
import { deleteObject, publicUrl, putObject } from "./storage";

export const MAX_BYTES = 8 * 1024 * 1024;        // per original file
export const MAX_PER_OWNER = { vendor: 12, service: 10, equipment: 10 } as const;
const MAX_SIDE = 1600;

export type OwnerKind = keyof typeof MAX_PER_OWNER;
export type Photo = { id: string; url: string; width: number; height: number; alt: string };

// Only real JPEG, PNG, WebP or HEIC images, checked by their first bytes, not the file name.
function sniff(b: Buffer) {
  if (b.length < 12) return null;
  if (b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return "jpeg";
  if (b.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))) return "png";
  if (b.subarray(0, 4).toString("ascii") === "RIFF" && b.subarray(8, 12).toString("ascii") === "WEBP") return "webp";
  if (b.subarray(4, 8).toString("ascii") === "ftyp" && /heic|heix|mif1|msf1/.test(b.subarray(8, 12).toString("ascii"))) return "heic";
  return null;
}

/** The vendor that owns the thing, if the signed-in user owns that vendor. */
async function ownerVendor(kind: OwnerKind, ownerId: string, userId: string) {
  const sql = kind === "vendor" ? `select v.id from vendors v where v.id = $1 and v.owner_id = $2`
    : kind === "service" ? `select v.id from services s join vendors v on v.id = s.vendor_id where s.id = $1 and v.owner_id = $2`
    : `select v.id from equipment e join vendors v on v.id = e.vendor_id where e.id = $1 and v.owner_id = $2`;
  return (await one<{ id: string }>(sql, [ownerId, userId]))?.id ?? null;
}

export async function uploadPhotos(userId: string, kind: OwnerKind, ownerId: string, files: File[]): Promise<{ added: number; errors: string[] }> {
  const vendorId = await ownerVendor(kind, ownerId, userId);
  if (!vendorId) return { added: 0, errors: ["You can only add photos to your own business."] };
  const count = (await one<{ n: number }>(`select count(*)::int as n from media where owner_kind = $1 and owner_id = $2`, [kind, ownerId]))!.n;
  const room = MAX_PER_OWNER[kind] - count;
  const errors: string[] = []; let added = 0;
  if (room <= 0) return { added, errors: [`You already have ${MAX_PER_OWNER[kind]} photos here. Delete one to add another.`] };
  for (const f of files.slice(0, room)) {
    if (!f || f.size === 0) continue;
    if (f.size > MAX_BYTES) { errors.push(`${f.name}: larger than 8 MB.`); continue; }
    const raw = Buffer.from(await f.arrayBuffer());
    if (!sniff(raw)) { errors.push(`${f.name}: not a JPEG, PNG, WebP or HEIC photo.`); continue; }
    try {
      // Re-encode: fixes rotation, resizes, and drops all metadata (including GPS location).
      const { data, info } = await sharp(raw, { limitInputPixels: 60_000_000 }).rotate()
        .resize({ width: MAX_SIDE, height: MAX_SIDE, fit: "inside", withoutEnlargement: true }).webp({ quality: 80 }).toBuffer({ resolveWithObject: true });
      const key = `${vendorId}/${kind}/${crypto.randomUUID()}.webp`;
      await putObject(key, data, "image/webp");
      await pool.query(`insert into media (vendor_id, owner_kind, owner_id, storage_key, width, height, bytes, sort)
        values ($1,$2,$3,$4,$5,$6,$7, coalesce((select max(sort)+1 from media where owner_kind=$2 and owner_id=$3),0))`, [vendorId, kind, ownerId, key, info.width, info.height, data.length]);
      added++;
    } catch { errors.push(`${f.name}: could not read this image.`); }
  }
  if (files.length > room) errors.push(`Only ${room} more photo${room === 1 ? "" : "s"} fit here, so the rest were skipped.`);
  return { added, errors };
}

export async function deletePhoto(userId: string, mediaId: string) {
  const row = await one<{ key: string }>(`delete from media m using vendors v where m.id = $1 and v.id = m.vendor_id and v.owner_id = $2 returning m.storage_key as key`, [mediaId, userId]);
  if (row) await deleteObject(row.key);
  return !!row;
}

export async function makeCover(userId: string, mediaId: string) {
  await pool.query(`update media m set sort = -1 from vendors v where m.id = $1 and v.id = m.vendor_id and v.owner_id = $2`, [mediaId, userId]);
  await pool.query(`with o as (select m.owner_kind, m.owner_id from media m where m.id = $1)
    update media x set sort = r.rn from (select id, row_number() over (order by sort, created_at) - 1 as rn from media where (owner_kind, owner_id) = (select owner_kind, owner_id from o)) r where x.id = r.id`, [mediaId]);
}

const toPhoto = (r: { id: string; key: string; width: number; height: number; alt: string }): Photo => ({ id: r.id, url: publicUrl(r.key), width: r.width, height: r.height, alt: r.alt });

export async function photosFor(kind: OwnerKind, ownerId: string): Promise<Photo[]> {
  return (await q<{ id: string; key: string; width: number; height: number; alt: string }>(
    `select id, storage_key as key, width, height, alt from media where owner_kind = $1 and owner_id = $2 order by sort, created_at`, [kind, ownerId])).map(toPhoto);
}

/** First photo for each listing, for cards. */
export async function coversFor(items: { kind: "service" | "equipment"; id: string }[]): Promise<Map<string, Photo>> {
  if (!items.length) return new Map();
  const rows = await q<{ id: string; key: string; width: number; height: number; alt: string; owner_id: string }>(
    `select distinct on (owner_id) id, storage_key as key, width, height, alt, owner_id from media
     where (owner_kind, owner_id) in (select * from unnest($1::text[], $2::text[])) order by owner_id, sort, created_at`,
    [items.map(i => i.kind), items.map(i => i.id)]);
  return new Map(rows.map(r => [r.owner_id, toPhoto(r)]));
}
