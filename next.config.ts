import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The /preview/[slug] route reads its deed from data/preview/<slug>.json with
  // fs at request time. The path is built at runtime, so tracing cannot see it
  // and the files would be left out of the deployment.
  outputFileTracingIncludes: {
    "/preview/[slug]": ["./data/preview/**"],
  },
};

export default nextConfig;
