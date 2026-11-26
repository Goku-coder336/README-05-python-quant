import type { Config } from "tailwindcss";
const v = (n: string) => `var(--${n})`;
export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: v("bg"), paper: v("paper"), ink: v("text"), muted: v("text-muted"), line: v("line"),
        brown: { DEFAULT: v("brown"), on: v("on-brown") }, espresso: v("espresso"),
        caramel: { DEFAULT: v("caramel"), on: v("on-caramel") }, clay: { DEFAULT: v("clay"), on: v("on-clay") },
        latte: v("latte"), sand: v("sand"), blush: v("blush"), sage: v("sage"), "border-input": v("border-input"),
        success: v("success"), danger: v("danger"),
      },
      fontFamily: { display: ["var(--font-display)", "Georgia", "serif"], sans: ["var(--font-sans)", "system-ui", "sans-serif"] },
      transitionTimingFunction: { out: "cubic-bezier(0.22,1,0.36,1)" },
    },
  },
} satisfies Config;
