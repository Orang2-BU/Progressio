const base = (import.meta.env?.VITE_API_BASE_URL || '/api/v1/').replace(/\/?$/, '/');
let tokens = null;
let session = { user: null, reason: '' };
let version = 0;
let refreshing = null;
const listeners = new Set();

export class ApiError extends Error {
  constructor(message, status = 0, fields = {}) {
    super(message);
    this.status = status;
    this.fields = fields;
  }
}

export const subscribe = (listener) => { listeners.add(listener); return () => listeners.delete(listener); };
export const getSession = () => session;
function publish(user, reason = '') {
  session = { user, reason };
  listeners.forEach((listener) => listener());
}
export function logout(reason = '') {
  version += 1;
  tokens = null;
  refreshing = null;
  publish(null, reason);
}

async function send(path, { method = 'GET', body, access } = {}) {
  let response;
  try {
    response = await fetch(base + path, {
      method,
      headers: { Accept: 'application/json', ...(body !== undefined && { 'Content-Type': 'application/json' }),
        ...(access && { Authorization: `Bearer ${access}` }) },
      ...(body !== undefined && { body: JSON.stringify(body) }),
      credentials: 'omit',
      signal: AbortSignal.timeout(15000),
    });
  } catch {
    throw new ApiError('Tidak dapat terhubung ke server. Periksa koneksi dan coba lagi.');
  }
  let data;
  try { data = await response.json(); } catch {
    throw new ApiError('Server mengirim respons yang tidak dapat dibaca. Coba lagi.', response.status);
  }
  if (!response.ok) {
    const fields = Object.fromEntries(Object.entries(data || {})
      .filter(([key]) => key !== 'detail' && key !== 'code')
      .map(([key, value]) => [key, Array.isArray(value) ? value.join(' ') : String(value)]));
    throw new ApiError(data?.detail || fields.non_field_errors || 'Permintaan belum berhasil. Periksa isianmu.', response.status, fields);
  }
  return data;
}

export async function request(path, options = {}) {
  const currentVersion = version;
  const access = tokens?.access;
  if (!access) throw new ApiError('Masuk untuk melanjutkan.', 401);
  try {
    const data = await send(path, { ...options, access });
    if (currentVersion !== version) throw new ApiError('Sesi sudah berubah. Silakan masuk lagi.', 401);
    return data;
  } catch (error) {
    if (error.status !== 401 || currentVersion !== version) throw error;
  }
  if (tokens?.access === access) {
    if (!refreshing) {
      const pending = send('auth/refresh', { method: 'POST', body: { refresh: tokens.refresh } })
        .then((data) => {
          if (version !== currentVersion) throw new ApiError('Sesi sudah berakhir.', 401);
          if (!data.access) throw new ApiError('Respons sesi tidak valid. Masuk kembali.', 401);
          tokens = { ...tokens, access: data.access };
        }).catch((error) => {
          if (version === currentVersion && [400, 401, 403].includes(error.status)) {
            logout('Sesi berakhir. Masuk kembali untuk melanjutkan.');
          }
          throw error;
        }).finally(() => { if (refreshing === pending) refreshing = null; });
      refreshing = pending;
    }
    await refreshing;
  }
  if (version !== currentVersion || !tokens) throw new ApiError('Sesi sudah berakhir.', 401);
  try {
    const data = await send(path, { ...options, access: tokens.access });
    if (version !== currentVersion) throw new ApiError('Sesi sudah berakhir.', 401);
    return data;
  } catch (error) {
    if (version === currentVersion && error.status === 401) logout('Sesi berakhir. Masuk kembali untuk melanjutkan.');
    throw error;
  }
}

export const register = (body) => send('auth/register', { method: 'POST', body });
export async function login(body) {
  logout();
  const currentVersion = version;
  try {
    const data = await send('auth/login', { method: 'POST', body });
    if (version !== currentVersion) throw new ApiError('Proses masuk dibatalkan.', 401);
    if (!data.access || !data.refresh) throw new ApiError('Respons login tidak valid. Coba lagi.');
    tokens = data;
    const user = await request('auth/me');
    if (version !== currentVersion) throw new ApiError('Proses masuk dibatalkan.', 401);
    publish(user);
    return user;
  } catch (error) {
    if (version === currentVersion) logout();
    throw error;
  }
}

export async function reloadProfile() {
  const currentVersion = version;
  const user = await request('auth/me');
  if (version === currentVersion) publish(user);
  return user;
}
