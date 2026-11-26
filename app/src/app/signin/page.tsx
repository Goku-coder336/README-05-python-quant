import { redirect } from "next/navigation";
import { currentUser } from "@/lib/auth";
import { SignInForm } from "@/components/SignInForm";
export const metadata = { title: "Sign in" };
export default async function SignIn({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  const next = (await searchParams).next ?? "/account";
  if (await currentUser()) redirect(next.startsWith("/") && !next.startsWith("//") ? next : "/account");
  return (
    <div className="mx-auto max-w-md px-4 py-16 md:py-24">
      <p className="eyebrow">Welcome</p>
      <h1 className="mt-3 font-display text-4xl">Sign in to Utsella</h1>
      <p className="mt-2 text-muted">Same sign-in for planning an event and for running your business.</p>
      <div className="card mt-8 p-6"><SignInForm next={next} /></div>
    </div>
  );
}
