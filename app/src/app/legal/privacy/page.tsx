import { Fill, LegalPage } from "@/components/Legal";
export const metadata = { title: "Privacy policy" };
export default function Privacy() {
  return (
    <LegalPage title="Privacy policy" intro="This explains what personal data Festora collects, why, who we share it with, how long we keep it, and the choices you have.">
      <section><h2>1. Who is responsible</h2>
        <p><Fill>company legal name</Fill>, <Fill>registered address</Fill>, is responsible for your personal data on Festora. Questions or requests go to <Fill>privacy email</Fill> or our grievance officer on the <a className="underline" href="/contact">contact page</a>.</p></section>
      <section><h2>2. What we collect</h2>
        <ul><li><strong>Account:</strong> your email address, and your name if you add it.</li>
          <li><strong>Bookings:</strong> the name and WhatsApp number you give for a booking, dates, notes, prices, and the status of each booking.</li>
          <li><strong>Event plans:</strong> occasion, tradition you choose, city, guest count, date, budget, checklist and shortlist.</li>
          <li><strong>Vendors:</strong> business name, WhatsApp number, city, description, listings, photos, and notes from our verification check.</li>
          <li><strong>Waitlist:</strong> email, whether you are a customer or vendor, and your city.</li>
          <li><strong>Technical:</strong> a sign-in cookie, and limited request data such as IP address used to prevent abuse.</li></ul>
        <p>We remove location and camera data from every photo when it is uploaded. Choosing a tradition for an event plan is optional and only used to suggest a checklist.</p></section>
      <section><h2>3. Why we use it</h2>
        <ul><li>To provide the service you asked for: sign-in, event plans, bookings and messages between you and vendors.</li>
          <li>To send you emails about your bookings and account. We do not send marketing emails without your consent.</li>
          <li>To keep Festora safe: verifying vendors, preventing fraud and abuse, and settling disputes.</li>
          <li>To decide which cities to open next, using waitlist numbers.</li>
          <li>To meet legal duties such as tax and accounting records.</li></ul></section>
      <section><h2>4. Who we share it with</h2>
        <ul><li><strong>Vendors:</strong> when you request a booking, the vendor sees your name, WhatsApp number, dates and note. Their phone number is shown to you only after they accept.</li>
          <li><strong>Service providers who process data for us:</strong> Supabase (database and photo storage), Resend (email), <Fill>hosting provider, for example Vercel</Fill> (hosting), and, once payments launch, Razorpay and Stripe (payments). Later: Meta (WhatsApp messages), if you opt in.</li>
          <li><strong>Authorities:</strong> when the law requires it.</li></ul>
        <p>We do not sell personal data. Some providers store data outside your country. Where that happens we rely on the safeguards the law requires.</p></section>
      <section><h2>5. How long we keep it</h2>
        <ul><li>Account and event plans: until you delete your account.</li>
          <li>Booking records: <Fill>retention period, for example 8 years</Fill> after the booking, for tax and dispute reasons. If you delete your account, your name stays only on the vendor&apos;s copy of past bookings.</li>
          <li>Sign-in codes: 10 minutes. Sessions: up to 30 days.</li>
          <li>Waitlist: until we open in your city or you ask us to remove you.</li></ul></section>
      <section><h2>6. Your rights</h2>
        <p>Depending on where you live (for example India&apos;s Digital Personal Data Protection Act, 2023, the UK GDPR, or the UAE&apos;s data protection law), you can ask to access, correct or delete your data, withdraw consent, and complain to us or to your data protection authority. You can delete your account yourself from your account page. For anything else, contact us and we will reply within <Fill>response time, for example 30 days</Fill>.</p></section>
      <section><h2>7. Cookies</h2>
        <p>We use one essential cookie to keep you signed in. We do not use advertising or tracking cookies. If that changes, we will ask first.</p></section>
      <section><h2>8. Security</h2>
        <p>Sign-in codes and session tokens are stored only in scrambled (hashed) form, connections are encrypted, and access to vendor and booking data is checked on every request. No system is perfectly secure; if a breach affects you, we will tell you and the authorities as the law requires.</p></section>
      <section><h2>9. Children</h2><p>Festora is not meant for anyone under 18, and we do not knowingly collect their data.</p></section>
      <section><h2>10. Changes</h2><p>We will post updates here and tell you by email if a change matters.</p></section>
    </LegalPage>
  );
}
