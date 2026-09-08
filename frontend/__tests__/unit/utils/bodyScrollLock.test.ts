import { acquireBodyScrollLock, releaseBodyScrollLock } from 'utils/bodyScrollLock'

describe('bodyScrollLock', () => {
  beforeEach(() => {
    document.body.style.overflow = ''
    releaseBodyScrollLock()
    releaseBodyScrollLock()
  })

  it('keeps body scroll locked until all overlays release their lock', () => {
    acquireBodyScrollLock()
    expect(document.body.style.overflow).toBe('hidden')

    acquireBodyScrollLock()
    releaseBodyScrollLock()
    expect(document.body.style.overflow).toBe('hidden')

    releaseBodyScrollLock()
    expect(document.body.style.overflow).toBe('')
  })
})
