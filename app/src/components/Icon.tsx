import { Briefcase, Cake, Camera, Car, ClipboardText, CookingPot, Drop, FlowerLotus, Diamond, HandPalm, Heart, Lightbulb, Lightning, MicrophoneStage, MusicNotes, PaintBrush, SpeakerHifi, VideoCamera, Sparkle } from "@phosphor-icons/react/dist/ssr";

const map = { Briefcase, Cake, Camera, Car, ClipboardText, CookingPot, Drop, FlowerLotus, Diamond, HandPalm, Heart, Lightbulb, Lightning, MicrophoneStage, MusicNotes, PaintBrush, SpeakerHifi, Sparkle, VideoCamera } as const;

export function CategoryIcon({ name, size = 22 }: { name: string; size?: number }) {
  const C = (map as Record<string, typeof Sparkle>)[name] ?? Sparkle;
  return <C size={size} aria-hidden />;
}
