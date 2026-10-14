import { fileURLToPath } from 'node:url';

const backend = (process.env.API_PROXY_TARGET || 'http://127.0.0.1:8000').replace(/\/$/, '');
const frontendRoot = fileURLToPath(new URL('.', import.meta.url));

export default {
  // The repository has a separate root lockfile; keep Next resolution scoped to this app.
  turbopack: { root: frontendRoot },
  // Django mixes slash-ended list endpoints with slashless auth/detail endpoints.
  skipTrailingSlashRedirect: true,
  agentRules: false,
  async rewrites() {
    return [
      { source: '/api/:path*/', destination: `${backend}/api/:path*/` },
      { source: '/api/:path*', destination: `${backend}/api/:path*` },
    ];
  },
};
