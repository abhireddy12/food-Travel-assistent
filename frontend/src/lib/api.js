const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

async function safeJson(response) {
  try {
    return await response.json();
  } catch (error) {
    return {};
  }
}

export async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method || 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    body: options.body && typeof options.body !== 'string' ? JSON.stringify(options.body) : options.body,
  });

  if (!response.ok) {
    const data = await safeJson(response);
    throw new Error(data.error || 'Something went wrong.');
  }

  return response.json();
}

export { API_BASE_URL };
