import type { Config } from "tailwindcss";
const v = (n: string) => `var(--${n})`;
export default {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: v("bg"), surface: v("surface"), border: v("border"), "border-input": v("border-input"),
        text: v("text"), muted: v("text-muted"),
        accent: { DEFAULT: v("accent"), hover: v("accent-hover"), soft: v("accent-soft"), "on-soft": v("on-accent-soft") },
        "on-accent": v("on-accent"),
        highlight: { DEFAULT: v("highlight"), on: v("on-highlight") },
        whatsapp: { DEFAULT: v("whatsapp"), on: v("on-whatsapp") },
        danger: v("danger"), success: v("success"), warning: v("warning"), focus: v("focus"),
      },
      fontFamily: { display: v("font-display").split(","), sans: v("font-sans").split(",") },
      fontSize: { xs: ["12px","16px"], sm: ["14px","20px"], base: ["16px","24px"], lg: ["20px","28px"], xl: ["28px","34px"], display: ["40px","46px"] },
      borderRadius: { sm: v("radius-sm"), md: v("radius-md"), lg: v("radius-lg"), pill: v("radius-pill") },
      boxShadow: { card: v("shadow-card"), pop: v("shadow-pop") },
      maxWidth: { content: "1200px" },
    },
  },
} satisfies Config;
