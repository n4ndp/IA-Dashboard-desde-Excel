// ── API Base Layer ──
// Generic fetch wrapper with typed error handling.

export class ApiError extends Error {
  status: number
  detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

const BASE_URL = '/api'

async function parseErrorResponse(res: Response): Promise<string> {
  try {
    const body = await res.json()
    return body.detail ?? `Error ${res.status}`
  } catch {
    return `Error ${res.status}`
  }
}

export async function request<T>(
  method: string,
  path: string,
  options?: {
    body?: FormData | Record<string, unknown>
  },
): Promise<T> {
  const isFormData = options?.body instanceof FormData

  let headers: Record<string, string> | undefined
  let body: BodyInit | undefined

  if (options?.body) {
    if (isFormData) {
      body = options.body as FormData
    } else {
      headers = { 'Content-Type': 'application/json' }
      body = JSON.stringify(options.body)
    }
  }

  try {
    const res = await fetch(`${BASE_URL}${path}`, { method, headers, body })

    if (!res.ok) {
      const detail = await parseErrorResponse(res)
      throw new ApiError(res.status, detail)
    }

    // 204 No Content
    if (res.status === 204) {
      return undefined as T
    }

    return res.json() as Promise<T>
  } catch (err) {
    if (err instanceof ApiError) throw err
    throw new ApiError(0, 'Network error')
  }
}
