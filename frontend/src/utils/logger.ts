// import { ENVIRONMENT } from 'utils/credentials'
// import { logCriticalMessage, logException } from 'utils/helpers/sentry.config'

// export const logger = {
//   log: (...args: unknown[]) => {
//     const message = args
//       .map((arg) => (typeof arg === 'string' ? arg : JSON.stringify(arg)))
//       .join(' ')
//     console.log(message)
//   },

//   error: (...args: unknown[]) => {
//     if (ENVIRONMENT === 'development' || ENVIRONMENT === 'local') {
//       console.error(...args)
//     } else {
//       args.forEach((arg) => {
//         if (arg instanceof Error) {
//           logException(arg)
//         } else {
//           const message = typeof arg === 'string' ? arg : JSON.stringify(arg)
//           logCriticalMessage(message)
//         }
//       })
//     }
//   },
// }

// export default logger
