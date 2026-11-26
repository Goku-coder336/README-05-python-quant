import type { Metadata } from "next";
import Link from "next/link";
import { Fraunces, Manrope } from "next/font/google";
import "./globals.css";

const display = Fraunces({ subsets: ["latin"], variable: "--font-display", weight: ["400", "600"] });
const sans = Manrope({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: { default: "Festora", template: "%s | Festora" },
  description: "Book event services and rent professional gear in one place.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable}`}>
      <body className="min-h-screen">
        <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-brown focus:px-3 focus:py-2 focus:text-brown-on">Skip to content</a>
        <header className="sticky top-0 z-30 border-b border-line bg-bg/90 backdrop-blur">
          <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-4 md:px-8">
            <Link href="/" className="font-display text-2xl tracking-tight">Fest<span className="text-caramel">o</span>ra</Link>
            <nav aria-label="Main" className="flex items-center gap-2 text-sm font-medium sm:gap-5">
              <Link href="/explore" className="hidden hover:underline sm:inline">Explore cities</Link>
              <Link href="/vendor/join" className="btn-primary !px-4 !py-2">For vendors</Link>
            </nav>
          </div>
        </header>
        <main id="main">{children}</main>
        <footer className="mt-24 border-t border-line">
          <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-10 text-sm text-muted md:px-8">
            <span className="font-display text-xl text-ink">Fest<span className="text-caramel">o</span>ra</span>
            <span>Preview build. Sample vendors and prices.</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
