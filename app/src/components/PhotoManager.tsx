"use client";
import { useActionState, useRef, useState } from "react";
import { Star, Trash, UploadSimple } from "@phosphor-icons/react";
import { coverPhotoAction, deletePhotoAction, uploadPhotosAction, type PhotoState } from "@/app/actions";
type Photo = { id: string; url: string; width: number; height: number };

export function PhotoManager({ kind, ownerId, handle, photos, max, label }: { kind: "vendor" | "service" | "equipment"; ownerId: string; handle: string; photos: Photo[]; max: number; label: string }) {
  const [state, action, pending] = useActionState<PhotoState, FormData>(uploadPhotosAction, {});
  const [picked, setPicked] = useState(0); const ref = useRef<HTMLFormElement>(null);
  const id = `ph-${ownerId}`;
  return (
    <div className="grid gap-3">
      {photos.length > 0 ? (
        <ul className="grid grid-cols-3 gap-2 sm:grid-cols-4" aria-label={`${label} photos`}>
          {photos.map((p, i) => (
            <li key={p.id} className="group relative overflow-hidden rounded-2xl bg-latte">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={p.url} alt="" width={p.width} height={p.height} loading="lazy" className="aspect-square w-full object-cover" />
              {i === 0 && <span className="badge absolute left-1.5 top-1.5 bg-espresso/85 text-paper">Cover</span>}
              <div className="absolute inset-x-1.5 bottom-1.5 flex justify-end gap-1">
                {i > 0 && <form action={coverPhotoAction}><input type="hidden" name="mediaId" value={p.id} /><input type="hidden" name="handle" value={handle} /><button className="grid h-8 w-8 place-items-center rounded-full bg-paper/90 text-ink hover:bg-paper" aria-label={`Make photo ${i + 1} the cover`}><Star size={14} aria-hidden /></button></form>}
                <form action={deletePhotoAction}><input type="hidden" name="mediaId" value={p.id} /><input type="hidden" name="handle" value={handle} /><button className="grid h-8 w-8 place-items-center rounded-full bg-paper/90 text-danger hover:bg-paper" aria-label={`Delete photo ${i + 1}`}><Trash size={14} aria-hidden /></button></form>
              </div>
            </li>))}
        </ul>
      ) : <p className="text-sm text-muted">No photos yet. Listings with photos get far more requests.</p>}
      {photos.length < max && (
        <form ref={ref} action={async fd => { await action(fd); ref.current?.reset(); setPicked(0); }} className="flex flex-wrap items-center gap-2">
          <input type="hidden" name="kind" value={kind} /><input type="hidden" name="ownerId" value={ownerId} /><input type="hidden" name="handle" value={handle} />
          <label htmlFor={id} className="btn-line cursor-pointer !py-2"><UploadSimple size={16} aria-hidden />{picked ? `${picked} chosen` : "Choose photos"}</label>
          <input id={id} name="photos" type="file" accept="image/jpeg,image/png,image/webp,image/heic" multiple className="sr-only" onChange={e => setPicked(e.target.files?.length ?? 0)} />
          <button className="btn-primary !py-2" disabled={pending || !picked}>{pending ? "Uploading…" : "Upload"}</button>
          <span className="text-xs text-muted">{photos.length} of {max} · JPEG, PNG, WebP or HEIC up to 8 MB. Location data is removed.</span>
        </form>
      )}
      {state.error && <p role="alert" className="text-sm text-danger">{state.error}</p>}
      {state.ok && <p role="status" className="text-sm text-success">{state.ok}</p>}
    </div>
  );
}
