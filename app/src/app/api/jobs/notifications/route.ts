import { NextResponse } from "next/server";
import { processOutbox } from "@/lib/notify";
// Retries pending notifications. Call every few minutes from a scheduler (Vercel Cron, Supabase cron)
// with header "Authorization: Bearer <CRON_SECRET>".
export async function POST(req: Request) {
  const secret = process.env.CRON_SECRET;
  if (!secret || req.headers.get("authorization") !== `Bearer ${secret}`) return NextResponse.json({ error: "Not allowed" }, { status: 401 });
  return NextResponse.json(await processOutbox(50));
}
