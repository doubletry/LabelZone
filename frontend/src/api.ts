export interface HealthResponse {
  status: string
  message: string
}

export async function fetchHealth(locale: string): Promise<HealthResponse> {
  const response = await fetch(`/api/health?locale=${encodeURIComponent(locale)}`)
  if (!response.ok) throw new Error('Health check failed')
  return response.json() as Promise<HealthResponse>
}
