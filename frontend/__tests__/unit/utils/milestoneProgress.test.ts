import { FaCircleCheck, FaClock, FaUserGear } from 'react-icons/fa6'

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
    test('returns FaCircleCheck when progress is 100', () => {
      expect(getMilestoneProgressIcon(100)).toBe(FaCircleCheck)
    })

    test('returns FaUserGear when progress is between 1 and 99', () => {
      expect(getMilestoneProgressIcon(50)).toBe(FaUserGear)
    })

    test('returns FaClock when progress is 0', () => {
      expect(getMilestoneProgressIcon(0)).toBe(FaClock)
    })
  })
})
