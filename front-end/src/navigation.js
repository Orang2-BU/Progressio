export function loginDestination(next) {
  if (!next || !next.startsWith('/') || next.startsWith('//')) return '/';
  const url = new URL(next, 'https://progressio.local');
  const path = url.pathname.replace(/\/$/, '') || '/';
  if (url.origin !== 'https://progressio.local' || !['/', '/profile', '/catalog', '/diagnostic', '/diagnostic/result'].includes(path)) return '/';
  return path + url.search;
}
