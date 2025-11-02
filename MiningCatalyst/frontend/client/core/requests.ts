function getAxios() {
  return window.$nuxt.$axios
}

function buildUrl(url: string, path?: Object) {
  if (path) {
    Object.entries(path).forEach(([key, value]) => {
      url = url.replace(`{${key}}`, value)
    })
  }
  return url
}

const ABORTERS = {} as Record<string, AbortController>

export function makeRequest<T>({
  url,
  path,
  query,
  body,
  method,
  aborter_key = null,
  date_fields = [],
}: {
  url: string
  path?: Object
  query?: Object
  body?: Object
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  aborter_key?: string | boolean | null
  date_fields?: string[]
}): Promise<T> {
  if (aborter_key === true) {
    aborter_key = url
  }

  if (aborter_key) {
    if (ABORTERS[aborter_key]) {
      ABORTERS[aborter_key].abort()
    }
    ABORTERS[aborter_key] = new AbortController()
  }

  const signal = aborter_key ? ABORTERS[aborter_key].signal : null

  return getAxios().$request({
    url: buildUrl(url, path),
    method,
    params: query,
    data: body,
    // @ts-ignore
    signal,
  })
}

function formatDates<T>(obj: T, paths: string[]): T {
  if (Array.isArray(obj)) {
    return obj.map((item) => formatDates(item, paths)) as any
  } else {
    for (const path of paths) {
      const items = path.split('.').slice(1)
      processPath(obj, items)
    }

    return obj
  }
}

function processPath(obj: any, items: string[]) {
  let key = items[0]

  if (items.length === 1) {
    obj[key] = new Date(obj[key])
  } else if (key.endsWith('[]')) {
    key = key.slice(0, -2)
    for (const item of obj[key]) {
      processPath(item, items.slice(1))
    }
  } else {
    processPath(obj[key], items.slice(1))
  }
}
