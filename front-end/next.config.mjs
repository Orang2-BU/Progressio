const backend = (process.env.API_PROXY_TARGET || 'http://127.0.0.1:8000').replace(/\/$/, '');

export default {
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
