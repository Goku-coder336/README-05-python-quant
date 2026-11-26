import { redirect } from "next/navigation";
import { currentUser } from "@/lib/auth";
import { cities, countries, region, traditions } from "@/lib/data";
import { eventTypes } from "@/lib/planner";
import { PlanForm } from "@/components/PlanForm";
export const metadata = { title: "Plan your event" };
export default async function Plan() {
  if (!(await currentUser())) redirect("/signin?next=/plan");
  const [cs, ctry, types, trads] = await Promise.all([cities(), countries(), eventTypes(), traditions()]);
  const list = await Promise.all(cs.map(async c => ({ id: c.id, name: c.name, group: `${(await region(c.parentId!))?.name}, ${ctry.find(x => x.code === c.countryCode)?.name}` })));
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 md:py-20">
      <p className="eyebrow">Event planner</p>
      <h1 className="mt-3 font-display text-4xl md:text-5xl">Start your plan</h1>
      <p className="mt-3 text-lg text-muted">Tell us the occasion and we build a checklist for it, from the first look to the last dance. You can change everything later.</p>
      <div className="card mt-8 p-6 md:p-8"><PlanForm types={types} traditions={trads} cities={list} /></div>
    </div>
  );
}
