import { readLocal } from "@/lib/storage";
// Serves locally stored photos in development. In production photos come from Supabase Storage's own domain.
export async function GET(_: Request, { params }: { params: Promise<{ key: string[] }> }) {
  const key = (await params).key.join("/");
  if (!/^[\w-]+\/(vendor|service|equipment)\/[\w-]+\.webp$/.test(key)) return new Response("Not found", { status: 404 });
  const body = await readLocal(key);
  if (!body) return new Response("Not found", { status: 404 });
  return new Response(new Uint8Array(body), { headers: { "Content-Type": "image/webp", "Cache-Control": "public, max-age=31536000, immutable", "X-Content-Type-Options": "nosniff" } });
}
