import { Camera, ClipboardText, CookingPot, FlowerLotus, Lightbulb, Lightning, PaintBrush, SpeakerHifi, VideoCamera, Sparkle } from "@phosphor-icons/react/dist/ssr";

const map = { Camera, ClipboardText, CookingPot, FlowerLotus, Lightbulb, Lightning, PaintBrush, SpeakerHifi, VideoCamera } as const;

export function CategoryIcon({ name, size = 22 }: { name: string; size?: number }) {
  const C = (map as Record<string, typeof Sparkle>)[name] ?? Sparkle;
  return <C size={size} aria-hidden />;
}
