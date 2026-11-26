/** @type {import('next').NextConfig} */
export default {
  // Marketing landing page (built in replica/landing) serves the home route.
  async rewrites() { return [{ source: "/", destination: "/landing.html" }]; },
};
