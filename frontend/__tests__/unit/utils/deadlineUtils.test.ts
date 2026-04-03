import { getDeadlineCategory, DEADLINE_ALL, DEADLINE_OPTIONS } from 'utils/deadlineUtils'

describe('deadlineUtils', () => {
  describe('Constants', () => {
    it('should have DEADLINE_ALL constant', () => {
      expect(DEADLINE_ALL).toBe('all')
    })

    it('should have DEADLINE_OPTIONS with all required keys', () => {
      expect(DEADLINE_OPTIONS).toEqual([
        { key: 'all', label: 'All' },
        { key: 'overdue', label: 'Overdue' },
        { key: 'due-soon', label: 'Due Soon' },
        { key: 'upcoming', label: 'Upcoming' },
        { key: 'no-deadline', label: 'No Deadline' },
      ])
    })
  })

  describe('getDeadlineCategory', () => {
    it('should return "no-deadline" for null deadline', () => {
      expect(getDeadlineCategory(null)).toBe('no-deadline')
    })

    it('should return "overdue" for past deadlines', () => {
      const oneWeekAgo = new Date()
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
      const deadline = oneWeekAgo.toISOString()

      expect(getDeadlineCategory(deadline)).toBe('overdue')
    })

    it('should return "overdue" for yesterday deadline', () => {
      const yesterday = new Date()
      yesterday.setDate(yesterday.getDate() - 1)
      const deadline = yesterday.toISOString()

      expect(getDeadlineCategory(deadline)).toBe('overdue')
    })

    it('should return "due-soon" for deadline today', () => {
      const today = new Date()
      const deadline = today.toISOString()

      expect(getDeadlineCategory(deadline)).toBe('due-soon')
    })

    it('should return "due-soon" for deadline within 7 days', () => {
      const threeDaysFromNow = new Date()
      threeDaysFromNow.setDate(threeDaysFromNow.getDate() + 3)
      const deadline = threeDaysFromNow.toISOString()

      expect(getDeadlineCategory(deadline)).toBe('due-soon')
    })

    it('should return "due-soon" for deadline exactly 7 days from now', () => {
      const sevenDaysFromNow = new Date()
      sevenDaysFromNow.setDate(sevenDaysFromNow.getDate() + 7)
      const deadline = sevenDaysFromNow.toISOString()

      expect(getDeadlineCategory(deadline)).toBe('due-soon')
    })

    it('should return "upcoming" for deadline more than 7 days away', () => {
      const eightDaysFromNow = new Date()
      eightDaysFromNow.setDate(eightDaysFromNow.getDate() + 8)
      const deadline = eightDaysFromNow.toISOString()

      expect(getDeadlineCategory(deadline)).toBe('upcoming')
    })

    it('should return "upcoming" for deadline far in future', () => {
      const threeMonthsFromNow = new Date()
      threeMonthsFromNow.setMonth(threeMonthsFromNow.getMonth() + 3)
      const deadline = threeMonthsFromNow.toISOString()

      expect(getDeadlineCategory(deadline)).toBe('upcoming')
    })

    it('should ignore time component and only compare dates', () => {
      const today = new Date()
      const earlyMorning = new Date(
        Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate(), 0, 0, 0)
      )
      const lateNight = new Date(
        Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate(), 23, 59, 59)
      )

      expect(getDeadlineCategory(earlyMorning.toISOString())).toBe('due-soon')
      expect(getDeadlineCategory(lateNight.toISOString())).toBe('due-soon')
    })

    it('should handle timezone properly using UTC', () => {
      const tomorrow = new Date()
      tomorrow.setUTCDate(tomorrow.getUTCDate() + 1)
      const deadline = new Date(
        tomorrow.getUTCFullYear(),
        tomorrow.getUTCMonth(),
        tomorrow.getUTCDate()
      ).toISOString()

      expect(getDeadlineCategory(deadline)).toBe('due-soon')
    })

    it('should handle date string without timezone specifier', () => {
      const futureDate = new Date()
      futureDate.setDate(futureDate.getDate() + 15)
      const dateString = futureDate.toISOString().split('T')[0]

      expect(getDeadlineCategory(dateString)).toBe('upcoming')
    })
  })
})
