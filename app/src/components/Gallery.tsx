"use client";
import { useState } from "react";
type Photo = { id: string; url: string; width: number; height: number };
export function Gallery({ photos, title, dark }: { photos: Photo[]; title: string; dark?: boolean }) {
  const [i, setI] = useState(0);
  if (!photos.length) return <div className={`h-64 rounded-3xl md:h-96 ${dark ? "bg-espresso" : "bg-latte"}`} role="img" aria-label="No photos yet" />;
  const p = photos[i];
  return (
    <div>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={p.url} alt={`${title}, photo ${i + 1} of ${photos.length}`} width={p.width} height={p.height} className="h-64 w-full rounded-3xl bg-latte object-cover md:h-96" />
      {photos.length > 1 && (
        <ul className="mt-2 flex gap-2 overflow-x-auto p-1" aria-label="Choose a photo">
          {photos.map((x, n) => (
            <li key={x.id} className="shrink-0"><button onClick={() => setI(n)} aria-label={`Show photo ${n + 1}`} aria-current={n === i} className={`block overflow-hidden rounded-xl ring-2 transition ${n === i ? "ring-brown" : "ring-transparent opacity-70 hover:opacity-100"}`}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={x.url} alt="" width={80} height={80} loading="lazy" className="h-16 w-16 object-cover md:h-20 md:w-20" />
            </button></li>))}
        </ul>
      )}
    </div>
  );
}
