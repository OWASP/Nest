import { FaCircleCheck, FaClock, FaUserGear } from 'react-icons/fa6'
import { IconType } from'react-icons'
// helper functions used in about/page.tsx
export const getMilestoneProgressText = (progress: number): string => {
  if (progress === 100) {
    return 'Completed'
  } else if (progress > 0) {
    return 'In Progress'
  } else {
    return 'Not Started'
  }
}

export const getMilestoneProgressIcon = (progress: number) : IconType => {
  if (progress === 100) {
    return FaCircleCheck
  } else if (progress > 0) {
    return FaUserGear
  } else {
    return FaClock
  }
}
