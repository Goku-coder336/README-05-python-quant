// Sends one email through Resend. In development without a key, prints it to the server log instead.
export async function sendEmail(to: string, subject: string, text: string) {
  const key = process.env.RESEND_API_KEY;
  if (!key) {
    if (process.env.NODE_ENV === "production") throw new Error("RESEND_API_KEY is not set.");
    console.log(`[dev email] to=${to} subject="${subject}"\n${text}\n[/dev email]`);
    return;
  }
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: process.env.EMAIL_FROM, to, subject, text }),
  });
  if (!r.ok) throw new Error(`Email provider returned ${r.status}`);
}
