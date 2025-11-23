import { faCircleCheck, faClock, faUserGear } from '@fortawesome/free-solid-svg-icons'

import { getMilestoneProgressIcon, getMilestoneProgressText } from 'utils/milestoneProgress'

describe('milestone progress helpers', () => {
  describe('getMilestoneProgressText', () => {
    test('returns "Completed" when progress is 100', () => {
      expect(getMilestoneProgressText(100)).toBe('Completed')
    })

    test('returns "In Progress" when progress is between 1 and 99', () => {
      expect(getMilestoneProgressText(50)).toBe('In Progress')
    })

    test('returns "Not Started" when progress is 0', () => {
      expect(getMilestoneProgressText(0)).toBe('Not Started')
    })
  })

  describe('getMilestoneProgressIcon', () => {
    test('returns faCircleCheck when progress is 100', () => {
      expect(getMilestoneProgressIcon(100)).toBe(faCircleCheck)
    })

    test('returns faUserGear when progress is between 1 and 99', () => {
      expect(getMilestoneProgressIcon(50)).toBe(faUserGear)
    })

    test('returns faClock when progress is 0', () => {
      expect(getMilestoneProgressIcon(0)).toBe(faClock)
    })
  })
})
