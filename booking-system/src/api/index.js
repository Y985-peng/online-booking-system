import request from '../utils/request'

export const userApi = {
  login: (data) => request.post('/auth/login', data),
  register: (data) => request.post('/auth/register', data),
}

export const serviceApi = {
  getList: (params) => request.get('/services/', { params }),
  getDetail: (id) => request.get(`/services/${id}/`),
  publish: (data) => request.post('/services/publish/', data),
  getMyServices: () => request.get('/services/my/'),
  update: (id, data) => request.put(`/services/${id}/manage/`, data),
  delete: (id) => request.delete(`/services/${id}/manage/`),
  getCategories: () => request.get('/services/categories/'),
}

export const bookingApi = {
  create: (data) => request.post('/appointments/', data),
  cancel: (id) => request.post(`/appointments/${id}/cancel/`),
  confirm: (id) => request.post(`/appointments/${id}/confirm/`),
  pay: (id) => request.post(`/appointments/${id}/pay/`),
  getList: (params) => request.get('/appointments/my/', { params }),
}

export const reviewApi = {
  create: (data) => request.post('/reviews/', data),
  getList: (serviceId) => request.get(`/reviews/service/${serviceId}/`),
}

export const dashboardApi = {
  getStats: () => request.get('/services/dashboard/'),
}

export const timeSlotApi = {
  getList: () => request.get('/services/time-slots/'),
  create: (data) => request.post('/services/time-slots/', data),
  delete: (id) => request.delete(`/services/time-slots/${id}/`),
}

export const paymentApi = {
  getPayInfo: (data) => request.post('/payments/alipay/', data),
  mockPay: (data) => request.post('/payments/mock-pay/', data),
}

export const adminApi = {
  getUsers: (params) => request.get('/auth/admin/users/', { params }),
  getStats: () => request.get('/auth/admin/stats/'),
}

export const chatApi = {
  getConversations: () => request.get('/chat/conversations/'),
  createConversation: (data) => request.post('/chat/conversations/', data),
  getMessages: (id) => request.get(`/chat/conversations/${id}/messages/`),
  sendMessage: (id, data) => request.post(`/chat/conversations/${id}/messages/`, data),
}

export const postApi = {
  getList: () => request.get('/posts/'),
  create: (data) => request.post('/posts/', data),
  getMyPosts: () => request.get('/posts/my/'),
  getUserPosts: (uid) => request.get(`/posts/user/${uid}/`),
  follow: (uid) => request.post(`/posts/follow/${uid}/`),
  getFollowStats: (uid) => request.get(`/posts/follow/stats/${uid}/`),
}
