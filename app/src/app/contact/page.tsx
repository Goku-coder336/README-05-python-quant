import { Fill, LegalPage } from "@/components/Legal";
export const metadata = { title: "Contact and grievances" };
export default function Contact() {
  return (
    <LegalPage title="Contact and grievances" intro="How to reach Festora, and how to raise a complaint.">
      <section><h2>General questions</h2>
        <ul><li>Email: <Fill>support email</Fill></li><li>WhatsApp: <Fill>support WhatsApp number</Fill></li><li>Hours: <Fill>support hours and time zone</Fill></li></ul></section>
      <section><h2>Business details</h2>
        <ul><li><Fill>company legal name</Fill></li><li><Fill>registered address</Fill></li><li><Fill>GSTIN, if registered</Fill></li></ul></section>
      <section><h2>Grievance officer</h2>
        <p>For complaints about content, a vendor or customer, your personal data, or a booking we could not resolve:</p>
        <ul><li>Name: <Fill>grievance officer name</Fill></li><li>Email: <Fill>grievance email</Fill></li><li>Address: <Fill>postal address</Fill></li></ul>
        <p>We acknowledge complaints within <Fill>acknowledgement time</Fill> and aim to resolve them within <Fill>resolution time</Fill>. Tell us your account email, the booking reference if there is one, and what happened.</p></section>
    </LegalPage>
  );
}
