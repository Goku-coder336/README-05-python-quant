import { NextResponse } from "next/server";
import { z } from "zod";
import { joinWaitlist } from "@/lib/data";
import { limited } from "@/lib/ratelimit";

const Body = z.object({ email: z.string().trim().toLowerCase().email().max(254), role: z.enum(["customer", "vendor"]), city: z.string().trim().min(1).max(60) });

export async function POST(req: Request) {
  if (await limited("waitlist", 10, 3600_000)) return NextResponse.json({ error: "Too many sign-ups from this connection. Try again later." }, { status: 429 });
  const p = Body.safeParse(await req.json().catch(() => null));
  if (!p.success) return NextResponse.json({ error: "Check your email and city." }, { status: 400 });
  await joinWaitlist(p.data.email, p.data.role, p.data.city);
  return NextResponse.json({ ok: true });
}
