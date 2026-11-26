import { NextResponse } from "next/server";
import { processOutbox, queueReviewReminders } from "@/lib/notify";
// Queues review reminders, then retries pending notifications. Call every few minutes from a scheduler (Vercel Cron, Supabase cron)
// with header "Authorization: Bearer <CRON_SECRET>".
export async function POST(req: Request) {
  return run(req);
}
// Vercel Cron sends GET with the same Authorization header.
export async function GET(req: Request) {
  return run(req);
}
async function run(req: Request) {
  const secret = process.env.CRON_SECRET;
  if (!secret || req.headers.get("authorization") !== `Bearer ${secret}`) return NextResponse.json({ error: "Not allowed" }, { status: 401 });
  const reminders = await queueReviewReminders();
  return NextResponse.json({ reminders, ...(await processOutbox(50)) });
}
