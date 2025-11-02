import { faCircleCheck, faClock, faUserGear } from '@fortawesome/free-solid-svg-icons'

export const getMilestoneProgressText = (progress: number): string => {
  if (progress === 100) {
    return 'Completed'
  } else if (progress > 0) {
    return 'In Progress'
  } else {
    return 'Not Started'
  }
}

export const getMilestoneProgressIcon = (progress: number) => {
  if (progress === 100) {
    return faCircleCheck
  } else if (progress > 0) {
    return faUserGear
  } else {
    return faClock
  }
}
