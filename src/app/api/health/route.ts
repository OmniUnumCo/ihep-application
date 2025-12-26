import { NextResponse } from "next/server";

/**
 * Health check endpoint for Cloud Run liveness and readiness probes
 * GET /api/health
 */
export async function GET() {
  const healthCheck = {
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || "development",
    version: process.env.npm_package_version || "1.1.0-alpha",
  };

  return NextResponse.json(healthCheck, { status: 200 });
}
