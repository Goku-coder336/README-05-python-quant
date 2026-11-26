import { CityListings } from "@/components/CityListings";
export default async function CityPage({ params, searchParams }: { params: Promise<{ country: string; city: string }>; searchParams: Promise<{ intimate?: string; tradition?: string; for?: string }> }) {
  const { country, city } = await params;
  return <CityListings countryCode={country} citySlug={city} sp={await searchParams} />;
}
