import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '../api/client'

interface AsyncState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

/**
 * Runs `fn` on mount and whenever it changes identity (so callers should
 * memoize it with useCallback), tracking loading/error state. Call `reload`
 * to re-run it, e.g. after a mutation elsewhere invalidates the data.
 */
export function useAsync<T>(fn: () => Promise<T>): AsyncState<T> & { reload: () => void } {
  const [state, setState] = useState<AsyncState<T>>({ data: null, loading: true, error: null })
  const [version, setVersion] = useState(0)

  useEffect(() => {
    let cancelled = false
    setState((prev) => ({ data: prev.data, loading: true, error: null }))

    fn()
      .then((data) => {
        if (!cancelled) {
          setState({ data, loading: false, error: null })
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          const message = err instanceof ApiError ? err.message : 'Something went wrong.'
          setState({ data: null, loading: false, error: message })
        }
      })

    return () => {
      cancelled = true
    }
  }, [fn, version])

  const reload = useCallback(() => setVersion((v) => v + 1), [])

  return { ...state, reload }
}
