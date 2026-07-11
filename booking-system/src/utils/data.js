/**
 * 从 API 响应中提取列表数据
 * 后端格式统一为 { code, data, message }
 * 其中 data 可能是分页对象 { count, results } 或直接数组 [...]
 */
export function extractList(res) {
  if (!res) return []
  if (Array.isArray(res)) return res
  // {code, data: {count, results}}
  if (res.data?.results) return res.data.results
  // {code, data: [...]}
  if (Array.isArray(res.data)) return res.data
  // DRF 分页格式（未包装）：{count, results}
  if (res.results) return res.results
  // 兜底
  return []
}

/**
 * 从 API 响应中提取对象数据
 */
export function extractData(res) {
  if (!res) return null
  // 后端自定义包装格式
  if (res.data && typeof res.data === 'object') return res.data
  return res
}
