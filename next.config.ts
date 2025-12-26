import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker/Cloud Run deployment
  output: "standalone",

  // React compiler for performance optimization
  reactCompiler: true,

  // Disable telemetry in production builds
  experimental: {
    // Optimize package imports for faster builds
  },
};

export default nextConfig;
