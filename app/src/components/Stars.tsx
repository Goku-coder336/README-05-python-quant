import { Star } from "@phosphor-icons/react/dist/ssr";
/** Read-only star display with a text equivalent for screen readers. */
export function Stars({ value, size = 16 }: { value: number; size?: number }) {
  return (
    <span className="inline-flex items-center gap-0.5 text-caramel" role="img" aria-label={`${value.toFixed(1).replace(/\.0$/, "")} out of 5 stars`}>
      {[1, 2, 3, 4, 5].map(n => <Star key={n} size={size} weight={value >= n - 0.25 ? "fill" : "regular"} aria-hidden />)}
    </span>
  );
}
