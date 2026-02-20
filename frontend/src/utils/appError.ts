// Non-UI error utility for Apollo Client and other core logic

export class AppError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
    this.name = 'AppError'
  }
}

export function handleAppError(error: Error) {
  // Log to console or send to a logging service
  // No UI side effects here
  // eslint-disable-next-line no-console
  console.error(error)
}
