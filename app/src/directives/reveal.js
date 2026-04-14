/**
 * Scroll reveal directive — Stripe-style staggered fade-in.
 * Usage: v-reveal on any element or container.
 * Children with .rv class get staggered reveal.
 */

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        // Stagger children with .rv class
        const children = entry.target.querySelectorAll('.rv')
        if (children.length) {
          children.forEach((child, i) => {
            setTimeout(() => child.classList.add('revealed'), i * 60)
          })
        } else {
          entry.target.classList.add('revealed')
        }
        observer.unobserve(entry.target)
      }
    })
  },
  { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
)

export const vReveal = {
  mounted(el) {
    el.classList.add('reveal-target')
    observer.observe(el)
  },
}
