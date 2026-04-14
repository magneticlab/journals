/**
 * Scroll reveal directive — Stripe-style staggered fade-in.
 * Handles both initial mount AND re-renders (route changes).
 */

function reveal(el) {
  // Skip if already revealed
  if (el.classList.contains('revealed')) return

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          requestAnimationFrame(() => {
            const children = el.querySelectorAll('.rv:not(.revealed)')
            children.forEach((child, i) => {
              setTimeout(() => child.classList.add('revealed'), i * 60)
            })
            el.classList.add('revealed')
          })
          observer.unobserve(el)
        }
      })
    },
    { threshold: 0.05, rootMargin: '50px 0px 0px 0px' }
  )

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      observer.observe(el)
    })
  })
}

function reset(el) {
  el.classList.remove('revealed')
  el.querySelectorAll('.rv').forEach(c => c.classList.remove('revealed'))
}

export const vReveal = {
  mounted(el) {
    el.classList.add('reveal-target')
    reveal(el)
  },
  // Re-trigger on updates (route changes reuse the component)
  updated(el) {
    // If element lost its revealed state (content changed), re-reveal
    if (!el.classList.contains('revealed')) {
      reveal(el)
    }
  },
}
