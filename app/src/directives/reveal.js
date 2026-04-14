/**
 * Scroll reveal directive — Stripe-style staggered fade-in.
 * Elements start invisible and fade in when scrolled into view.
 * If already in viewport on mount, reveals immediately.
 */

export const vReveal = {
  mounted(el) {
    el.classList.add('reveal-target')

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Small delay so CSS transition can kick in
            requestAnimationFrame(() => {
              const children = el.querySelectorAll('.rv')
              if (children.length) {
                children.forEach((child, i) => {
                  setTimeout(() => child.classList.add('revealed'), i * 60)
                })
              }
              el.classList.add('revealed')
            })
            observer.unobserve(el)
          }
        })
      },
      { threshold: 0.05, rootMargin: '50px 0px 0px 0px' }
    )

    // Delay observation slightly so initial opacity:0 is applied first
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        observer.observe(el)
      })
    })
  },
}
