export function scrollToAnchor(targetId: string, additionalOffset = 80): void {
  try {
    const element = document.getElementById(targetId)

    if (!element) {
      return
    }
    const anchorElement = element.querySelector('[data-anchor-title]')
    const headingHeight = anchorElement instanceof HTMLElement ? anchorElement.offsetHeight : 0
    const yOffset = -headingHeight - additionalOffset

    // Use modern window.scrollY instead of deprecated pageYOffset
    const y = element.getBoundingClientRect().top + window.scrollY + yOffset
    window.scrollTo({
      top: y,
      behavior: 'smooth',
    })
  } catch {
    // Silently handle scroll errors
  }
}

export const scrollToAnchorWithHistory = (targetId: string, updateHistory = true): void => {
  scrollToAnchor(targetId)

  if (updateHistory) {
    try {
      const href = `#${targetId}`
      window.history.pushState(null, '', href)
    } catch {
      // Silently handle history update errors
    }
  }
}
