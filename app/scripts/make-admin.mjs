// Gives an existing account the admin role. Usage: npm run make-admin -- you@example.com
// The person must have signed in once first.
import pg from "pg";
const email = (process.argv[2] ?? "").trim().toLowerCase();
if (!email) { console.error("Usage: npm run make-admin -- you@example.com"); process.exit(1); }
const c = new pg.Client({ connectionString: process.env.DATABASE_URL }); await c.connect();
const r = await c.query("update users set role = 'admin' where email = $1 returning email", [email]);
console.log(r.rowCount ? `${email} is now an admin` : `No account for ${email}. Sign in on the site once, then run this again.`);
await c.end();
