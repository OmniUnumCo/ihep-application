import { Provider, ProviderSearchFilters } from '@/types/provider'

export async function getProviders(filters?: ProviderSearchFilters): Promise<Provider[]> {
  const params = new URLSearchParams()

  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value))
      }
    })
  }

  const response = await fetch(`/api/providers?${params.toString()}`)

  if (!response.ok) {
    throw new Error('Failed to fetch providers')
  }

  return response.json()
}

export async function getProviderById(id: string): Promise<Provider> {
  const response = await fetch(`/api/providers/${id}`)

  if (!response.ok) {
    throw new Error('Failed to fetch provider')
  }

  return response.json()
}

export async function searchProviders(query: string, filters?: ProviderSearchFilters): Promise<Provider[]> {
  const params = new URLSearchParams({ q: query })

  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value))
      }
    })
  }

  const response = await fetch(`/api/providers/search?${params.toString()}`)

  if (!response.ok) {
    throw new Error('Failed to search providers')
  }

  return response.json()
}
