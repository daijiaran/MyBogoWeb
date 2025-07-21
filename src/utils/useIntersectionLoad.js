// src/composables/useIntersectionLoad.js
import { onMounted, onBeforeUnmount, ref } from 'vue'

/**
 * 通用懒加载 Hook（稳健版）
 *
 * @param {Ref<HTMLElement>} targetRef - 被观察的 DOM ref
 * @param {Function} callback - 元素进入视口时执行（可 async）
 * @param {Object} options - { root, rootMargin, threshold, fallbackDelay }
 * @returns {Object} { isVisible, forceLoad }
 */
export function useIntersectionLoad(targetRef, callback, options = {}) {
    const isVisible = ref(false)
    let observer = null

    const {
        root = null,
        rootMargin = '600px',
        threshold = 0.01,
        fallbackDelay = 6000
    } = options

    const observe = () => {
        if (!targetRef?.value) return

        if (!('IntersectionObserver' in window)) {
            // 不支持时直接触发
            isVisible.value = true
            try { callback?.() } catch (e) { /* swallow */ }
            return
        }

        observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        isVisible.value = true
                        try { callback?.() } catch (e) { /* swallow */ }
                        if (observer && entry.target) observer.unobserve(entry.target)
                    }
                })
            },
            { root, rootMargin, threshold }
        )

        observer.observe(targetRef.value)
        // debug
        // console.debug('[useIntersectionLoad] observe attached', targetRef.value)
    }

    // 兜底：fallbackDelay 后强制触发一次（仅当还没触发）
    const fallbackTimer = setTimeout(() => {
        if (!isVisible.value) {
            isVisible.value = true
            try { callback?.() } catch (e) { /* swallow */ }
            // debug
            // console.warn('[useIntersectionLoad] fallback triggered')
        }
    }, fallbackDelay)

    onMounted(observe)

    onBeforeUnmount(() => {
        if (observer) observer.disconnect()
        clearTimeout(fallbackTimer)
    })

    // 允许运行时强制触发加载
    const forceLoad = () => {
        if (!isVisible.value) {
            isVisible.value = true
            try { callback?.() } catch (e) { /* swallow */ }
        }
    }

    return { isVisible, forceLoad }
}
