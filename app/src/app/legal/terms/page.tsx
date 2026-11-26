import { Fill, LegalPage } from "@/components/Legal";
export const metadata = { title: "Terms of use" };
export default function Terms() {
  return (
    <LegalPage title="Terms of use" intro="These terms explain how Utsella works, what we do and do not do, and what we expect from customers and vendors. By creating an account or making a booking you agree to them.">
      <section><h2>1. Who we are</h2>
        <p>Utsella is run by <Fill>company legal name</Fill>, registered in <Fill>country and registration number</Fill>, with its registered office at <Fill>registered address</Fill> (&quot;Utsella&quot;, &quot;we&quot;, &quot;us&quot;). You can reach us through the <a className="underline" href="/contact">contact page</a>.</p></section>
      <section><h2>2. What Utsella is</h2>
        <p>Utsella is an online marketplace. It helps customers plan events and find, compare and book independent vendors: service providers (such as planners, makeup artists, photographers and caterers) and owners of rental equipment (such as sound, lighting and generators).</p>
        <p>Vendors are independent businesses. They are not our employees or agents. The contract for a service or rental is between the customer and the vendor. We provide the platform, the booking records and, once online payments launch, payment collection on the vendor&apos;s behalf.</p></section>
      <section><h2>3. Accounts</h2>
        <ul><li>You must be at least 18 years old, or the age of majority where you live, to create an account.</li>
          <li>Give accurate details and keep access to your email address secure. Anyone who signs in with your email code acts as you.</li>
          <li>You can sign out of all devices and delete your account at any time from your account page.</li></ul></section>
      <section><h2>4. Bookings</h2>
        <ul><li>A booking request is not confirmed until the vendor accepts it. We email you when they do.</li>
          <li>The price, advance, deposit, cancellation terms and what is included are shown on each listing before you request it. The vendor is responsible for delivering what the listing describes.</li>
          <li>Before online payments launch, any payment you make goes directly to the vendor and is outside Utsella.</li>
          <li>Cancellations and refunds follow our <a className="underline" href="/legal/refunds">refunds and cancellations policy</a> and the vendor&apos;s terms shown on the listing.</li></ul></section>
      <section><h2>5. Equipment rental</h2>
        <ul><li>The customer is responsible for rented equipment from handover until it is returned, including loss, theft and damage beyond normal wear.</li>
          <li>Both sides should record the equipment&apos;s condition at handover and at return. Photos taken in Utsella at those moments are used to settle disputes.</li>
          <li>Where a deposit applies, it is held and released or used as described in the refunds policy.</li>
          <li>Equipment that needs a trained operator may only be run by the vendor&apos;s technician or someone the vendor approves.</li></ul></section>
      <section><h2>6. Vendors</h2>
        <ul><li>Listing on Utsella is free unless we tell you otherwise in advance. Our commission and any plan fees will be shown before they apply to you.</li>
          <li>You must hold any licences, registrations and insurance your work needs, and only list services and equipment you can actually provide on the dates you accept.</li>
          <li>Only upload photos you took or have the right to use. We remove location data from photos automatically.</li>
          <li>The &quot;Verified&quot; badge means we checked your identity and business details at the time. It is not a guarantee of quality.</li>
          <li>Do not use customer contact details for anything other than the booking they relate to.</li></ul></section>
      <section><h2>7. What is not allowed</h2>
        <ul><li>False listings, fake reviews, or misleading prices.</li>
          <li>Taking a booking found on Utsella off the platform to avoid its protections or fees.</li>
          <li>Harassment, discrimination, or content that is unlawful or infringes someone else&apos;s rights.</li>
          <li>Scraping, automated access, or attempts to break or overload the service.</li></ul>
        <p>We may remove content, suspend or close accounts that break these terms, and tell the affected customer or vendor.</p></section>
      <section><h2>8. Our responsibility</h2>
        <p>We work to keep Utsella accurate and available but cannot promise it will always be uninterrupted. Vendors are responsible for their own services and equipment. To the extent the law allows, our total liability to you for any claim related to a booking is limited to the fees Utsella received for that booking. Nothing in these terms limits liability that cannot be limited by law, or your statutory rights as a consumer.</p></section>
      <section><h2>9. Disputes and governing law</h2>
        <p>If something goes wrong, contact the vendor first, then us through the <a className="underline" href="/contact">grievance contact</a>. These terms are governed by the laws of <Fill>governing law, for example India</Fill>, and the courts of <Fill>city</Fill> have jurisdiction, without removing any right you have to bring a claim where you live.</p></section>
      <section><h2>10. Changes</h2>
        <p>We may update these terms. If a change matters, we will tell you by email or on the site before it takes effect. The date at the top shows the latest version.</p></section>
    </LegalPage>
  );
}
