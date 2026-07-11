import axios from 'axios'

// 部署到云端后，把下面的地址改成你的 PythonAnywhere 网址
// 例如: https://你的用户名.pythonanywhere.com/api
const API_BASE = import.meta.env.VITE_API_URL || 'https://yunshenwanli.pythonanywhere.com/api'

const request = axios.create({
  baseURL: API_BASE,
  timeout: 30000
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

request.interceptors.response.use(
  response => response.data,
  error => {
    return Promise.reject(error)
  }
)

export default request
