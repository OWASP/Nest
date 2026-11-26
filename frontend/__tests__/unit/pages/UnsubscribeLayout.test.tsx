import { metadata } from 'app/unsubscribe/[token]/layout'

describe('UnsubscribeLayout metadata', () => {
  it('keeps token URLs out of search indexes', () => {
    expect(metadata.robots).toEqual({ index: false, follow: false })
  })

  it('does not emit a canonical URL', () => {
    expect(metadata.alternates?.canonical).toBeUndefined()
  })
})
