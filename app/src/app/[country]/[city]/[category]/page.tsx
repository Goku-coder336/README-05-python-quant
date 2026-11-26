import { CityListings } from "@/components/CityListings";
export default async function CategoryPage({ params, searchParams }: { params: Promise<{ country: string; city: string; category: string }>; searchParams: Promise<{ intimate?: string; tradition?: string }> }) {
  const { country, city, category } = await params;
  return <CityListings countryCode={country} citySlug={city} categorySlug={category} sp={await searchParams} />;
}
