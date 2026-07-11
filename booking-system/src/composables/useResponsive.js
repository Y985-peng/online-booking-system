import { ref, onMounted, onUnmounted } from 'vue'

export function useResponsive() {
  const isMobile = ref(true)
  const isDesktop = ref(false)

  const check = () => {
    isMobile.value = window.innerWidth < 768
    isDesktop.value = window.innerWidth >= 768
  }

  onMounted(() => {
    check()
    window.addEventListener('resize', check)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', check)
  })

  return { isMobile, isDesktop }
}
