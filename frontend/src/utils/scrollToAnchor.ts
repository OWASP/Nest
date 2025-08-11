export const scrollToAnchor = (targetId: string): void => {
  try {
    const element = document.getElementById(targetId)
    
    if (!element) {
      return
    }

    const headingHeight =
      (element.querySelector('div#anchor-title') as HTMLElement)?.offsetHeight || 0

    const yOffset = -headingHeight - 80
    
    // Use modern window.scrollY instead of deprecated pageYOffset
    const y = element.getBoundingClientRect().top + window.scrollY + yOffset

    window.scrollTo({ 
      top: y, 
      behavior: 'smooth' 
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