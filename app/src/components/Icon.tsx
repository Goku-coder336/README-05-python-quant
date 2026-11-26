import * as Icons from "@phosphor-icons/react/dist/ssr";
import type { ComponentType } from "react";

// Server-only: renders any Phosphor icon by name. Client components receive the rendered icon as a prop,
// so the icon set never ships to the browser.
type P = { size?: number; "aria-hidden"?: boolean };
export function CategoryIcon({ name, size = 22 }: { name: string; size?: number }) {
  const C = ((Icons as unknown as Record<string, ComponentType<P>>)[name]) ?? Icons.Sparkle;
  return <C size={size} aria-hidden />;
}

/** Icons admins can pick from when creating event types and categories. */
export const ICON_CHOICES = ["Sparkle","Heart","Diamond","Champagne","Baby","House","Coffee","Flower","FlowerLotus","Church","MoonStars","Bank","HandsPraying","Balloon","UsersThree","ForkKnife","Confetti","Presentation","RocketLaunch","Storefront","Mountains","Trophy","GraduationCap","SoccerBall","HandHeart","MusicNotes","Cake","Briefcase","Camera","VideoCamera","PaintBrush","HandPalm","CookingPot","ClipboardText","MicrophoneStage","Car","Buildings","Envelope","Gift","ShieldCheck","Broom","Flag","Broadcast","SpeakerHifi","Lightbulb","Lightning","Monitor","Cube","Tent","Armchair","Fan","Drop"] as const;
