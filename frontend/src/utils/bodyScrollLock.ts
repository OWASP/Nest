let lockCount = 0
let previousOverflow = ''

export const acquireBodyScrollLock = () => {
  if (lockCount === 0) {
    previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
  }
  lockCount++
}

export const releaseBodyScrollLock = () => {
  if (lockCount <= 0) {
    return
  }

  lockCount--
  if (lockCount === 0) {
    document.body.style.overflow = previousOverflow
    previousOverflow = ''
  }
}
