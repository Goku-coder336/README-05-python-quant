import { Fill, LegalPage } from "@/components/Legal";
export const metadata = { title: "Refunds and cancellations" };
export default function Refunds() {
  return (
    <LegalPage title="Refunds and cancellations" intro="What happens to your money when a booking is cancelled, by you or by the vendor, and how rental deposits work.">
      <section><h2>1. Before a booking is confirmed</h2>
        <p>Sending a request costs nothing. You can withdraw it from My bookings at any time before the vendor accepts.</p></section>
      <section><h2>2. If the vendor cancels or declines</h2>
        <p>You get a full refund of everything you paid through Festora, including any Festora fee. Refunds go back to the original payment method.</p></section>
      <section><h2>3. If you cancel a confirmed booking</h2>
        <p>Each listing shows the vendor&apos;s cancellation terms before you book. They decide how much of the advance is refunded and by when. As a guide, Festora asks vendors to offer at least:</p>
        <ul><li>A full refund of the advance if you cancel <Fill>N</Fill> days or more before the event.</li>
          <li>A partial refund of <Fill>percentage</Fill> if you cancel between <Fill>N</Fill> and <Fill>N</Fill> days before.</li>
          <li>No refund of the advance within <Fill>N</Fill> days of the event, unless the vendor agrees.</li></ul>
        <p>The Festora fee is <Fill>refundable or not refundable</Fill> when you cancel.</p></section>
      <section><h2>4. Rental deposits</h2>
        <ul><li>The deposit is held when the rental is confirmed and is not the vendor&apos;s income.</li>
          <li>It is released within <Fill>N</Fill> working days after the equipment is returned and checked, unless the vendor reports damage or loss.</li>
          <li>If damage is reported, the vendor must show photos from handover and return. We review both sides and may use part or all of the deposit to cover repair or replacement. You will see the reason and the amount.</li></ul></section>
      <section><h2>5. Events that cannot go ahead</h2>
        <p>If an event is stopped by events outside anyone&apos;s control, such as a government order or a natural disaster, we will help you and the vendor agree a new date or a fair refund.</p></section>
      <section><h2>6. How long refunds take</h2>
        <p>Once approved, refunds are sent within <Fill>N</Fill> working days. Your bank or card provider may take a few more days to show it.</p></section>
      <section><h2>7. Problems with a booking</h2>
        <p>If a service was not delivered as described, tell us within <Fill>N</Fill> days of the event through the <a className="underline" href="/contact">contact page</a>, with photos or messages if you have them.</p></section>
      <p className="text-sm text-muted">Online payments are not live yet. Until they are, any money you pay goes directly to the vendor under their own terms.</p>
    </LegalPage>
  );
}
