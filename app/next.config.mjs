/** @type {import('next').NextConfig} */
export default {
  // Marketing landing page (built in replica/landing) serves the home route.
  async rewrites() { return [{ source: "/", destination: "/landing.html" }]; },
  // Photo uploads go through server actions: up to 6 photos of 8 MB each per upload.
  experimental: { serverActions: { bodySizeLimit: "50mb" } },
};
