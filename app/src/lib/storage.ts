import fs from "node:fs/promises";
import path from "node:path";

// Object storage. Uses Supabase Storage when SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set,
// otherwise a local folder (development only; files are served by /media/[...key]).
const SB_URL = process.env.SUPABASE_URL?.replace(/\/$/, "");
const SB_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;
const BUCKET = process.env.SUPABASE_BUCKET || "media";
const LOCAL = path.join(process.cwd(), ".uploads");
const useSupabase = () => !!(SB_URL && SB_KEY);

function assertConfigured() {
  if (!useSupabase() && process.env.NODE_ENV === "production") throw new Error("Photo storage is not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.");
}

export async function putObject(key: string, body: Buffer, contentType: string) {
  assertConfigured();
  if (useSupabase()) {
    const r = await fetch(`${SB_URL}/storage/v1/object/${BUCKET}/${key}`, {
      method: "POST", headers: { Authorization: `Bearer ${SB_KEY}`, "Content-Type": contentType, "x-upsert": "false", "Cache-Control": "31536000" }, body: new Uint8Array(body),
    });
    if (!r.ok) throw new Error(`Upload failed (${r.status})`);
    return;
  }
  const file = path.join(LOCAL, key);
  await fs.mkdir(path.dirname(file), { recursive: true });
  await fs.writeFile(file, body);
}

export async function deleteObject(key: string) {
  if (useSupabase()) { await fetch(`${SB_URL}/storage/v1/object/${BUCKET}/${key}`, { method: "DELETE", headers: { Authorization: `Bearer ${SB_KEY}` } }); return; }
  await fs.rm(path.join(LOCAL, key), { force: true });
}

/** Public URL. Supabase serves from its own domain; local files come from /media. */
export function publicUrl(key: string) {
  return useSupabase() ? `${SB_URL}/storage/v1/object/public/${BUCKET}/${key}` : `/media/${key}`;
}

export async function readLocal(key: string) {
  const safe = path.normalize(key).replace(/^(\.\.(\/|\\|$))+/, "");
  const file = path.join(LOCAL, safe);
  if (!file.startsWith(LOCAL + path.sep)) return null;
  try { return await fs.readFile(file); } catch { return null; }
}
