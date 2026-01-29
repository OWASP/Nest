declare module 'isomorphic-dompurify' {
  const sanitize: (content: string) => string
  export default { sanitize }
}

declare module 'lodash';

declare module 'jest-axe' {
  interface AxeResults {
    violations: Array<{
      id: string
      impact?: string
      description: string
      nodes: Array<{ html: string }>
    }>
  }
  const axe: (html: Element | string) => Promise<AxeResults>
  const toHaveNoViolations: jest.CustomMatcher
  export { axe, toHaveNoViolations }
}
declare global {
  namespace jest {
    interface Matchers<R> {
      toHaveNoViolations(): R
    }
  }
}

export {}
