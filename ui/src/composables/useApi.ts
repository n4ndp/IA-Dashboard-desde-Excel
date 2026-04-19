const BASE_URL = '/api'

export async function apiPost<T = unknown>(endpoint: string, body: FormData | Record<string, unknown>): Promise<T> {
  const isFormData = body instanceof FormData
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    body: isFormData ? body : JSON.stringify(body),
    ...(!isFormData && { headers: { 'Content-Type': 'application/json' } }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Network error' }))
    throw new Error(err.detail || `Error ${res.status}`)
  }

  return res.json()
}

export async function apiGet<T = unknown>(endpoint: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${endpoint}`)

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Network error' }))
    throw new Error(err.detail || `Error ${res.status}`)
  }

  return res.json()
}

export async function apiPatch<T = unknown>(endpoint: string, body: Record<string, unknown>): Promise<T> {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Network error' }))
    throw new Error(err.detail || `Error ${res.status}`)
  }

  return res.json()
}

export async function apiDelete<T = unknown>(endpoint: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'DELETE',
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Network error' }))
    throw new Error(err.detail || `Error ${res.status}`)
  }

  // 204 No Content — no JSON body
  if (res.status === 204) {
    return undefined as T
  }

  return res.json()
}
