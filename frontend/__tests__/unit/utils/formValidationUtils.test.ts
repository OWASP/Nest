import {
  validateRequired,
  validateName,
  validateDescription,
  validateStartDate,
  validateEndDate,
  getCommonValidationRules,
} from 'components/forms/shared/formValidationUtils'

describe('formValidationUtils', () => {
  describe('validateRequired', () => {
    it('returns error message when value is empty string', () => {
      expect(validateRequired('', 'Field')).toBe('Field is required')
    })

    it('returns error message when value is only whitespace', () => {
      expect(validateRequired('   ', 'Field')).toBe('Field is required')
    })

    it('returns error message when value is null or undefined', () => {
      expect(validateRequired(null, 'Name')).toBe('Name is required')
      expect(validateRequired(undefined, 'Name')).toBe('Name is required')
    })

    it('returns undefined when value is valid', () => {
      expect(validateRequired('valid value', 'Field')).toBeUndefined()
    })

    it('returns undefined when value has leading/trailing spaces but content', () => {
      expect(validateRequired('  valid  ', 'Field')).toBeUndefined()
    })
  })

  describe('validateName', () => {
    it('returns required error when name is empty', () => {
      expect(validateName('')).toBe('Name is required')
    })

    it('returns required error when name is only whitespace', () => {
      expect(validateName('   ')).toBe('Name is required')
    })

    it('returns error when name exceeds 200 characters', () => {
      const longName = 'a'.repeat(201)
      expect(validateName(longName)).toBe('Name must be 200 characters or less')
    })

    it('returns undefined when name is exactly 200 characters', () => {
      const exactName = 'a'.repeat(200)
      expect(validateName(exactName)).toBeUndefined()
    })

    it('returns uniqueness error when provided', () => {
      expect(validateName('Valid Name', 'Name already exists')).toBe('Name already exists')
    })

    it('returns undefined when name is valid with no uniqueness error', () => {
      expect(validateName('Valid Name')).toBeUndefined()
    })

    it('returns undefined when uniqueness error is undefined', () => {
      expect(validateName('Valid Name', undefined)).toBeUndefined()
    })

    it('prioritizes required error over length error', () => {
      expect(validateName('')).toBe('Name is required')
    })

    it('prioritizes length error over uniqueness error', () => {
      const longName = 'a'.repeat(201)
      expect(validateName(longName, 'Name already exists')).toBe(
        'Name must be 200 characters or less'
      )
    })
  })

  describe('validateDescription', () => {
    it('returns error when description is empty', () => {
      expect(validateDescription('')).toBe('Description is required')
    })

    it('returns error when description is only whitespace', () => {
      expect(validateDescription('   ')).toBe('Description is required')
    })

    it('returns undefined when description is valid', () => {
      expect(validateDescription('Valid description')).toBeUndefined()
    })
  })

  describe('validateStartDate', () => {
    it('returns error when start date is empty', () => {
      expect(validateStartDate('')).toBe('Start date is required')
    })

    it('returns error when start date is only whitespace', () => {
      expect(validateStartDate('   ')).toBe('Start date is required')
    })

    it('returns undefined when start date is valid', () => {
      expect(validateStartDate('2024-01-01')).toBeUndefined()
    })
  })

  describe('validateEndDate', () => {
    it('returns error when end date is empty', () => {
      expect(validateEndDate('')).toBe('End date is required')
    })

    it('returns error when end date is only whitespace', () => {
      expect(validateEndDate('   ')).toBe('End date is required')
    })

    it('returns error when end date is before start date', () => {
      expect(validateEndDate('2024-01-01', '2024-06-01')).toBe('End date must be after start date')
    })

    it('returns error when end date equals start date', () => {
      expect(validateEndDate('2024-01-01', '2024-01-01')).toBe('End date must be after start date')
    })

    it('returns undefined when end date is after start date', () => {
      expect(validateEndDate('2024-06-01', '2024-01-01')).toBeUndefined()
    })

    it('returns undefined when start date is not provided', () => {
      expect(validateEndDate('2024-01-01')).toBeUndefined()
    })

    it('returns undefined when start date is undefined', () => {
      expect(validateEndDate('2024-01-01', undefined)).toBeUndefined()
    })

    it('returns undefined when start date is empty string', () => {
      expect(validateEndDate('2024-01-01', '')).toBeUndefined()
    })
  })

  describe('getCommonValidationRules', () => {
    const mockValidateName = jest.fn()
    const mockValidateEndDate = jest.fn()

    beforeEach(() => {
      jest.clearAllMocks()
      mockValidateName.mockReturnValue(undefined)
      mockValidateEndDate.mockReturnValue(undefined)
    })

    it('returns array with 4 validation rules', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = {}

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )

      expect(rules).toHaveLength(4)
    })

    it('sets shouldValidate based on touched state for name', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = { name: true }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )

      expect(rules[0].shouldValidate).toBe(true)
    })

    it('sets shouldValidate false when name is not touched', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = { name: false }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )

      expect(rules[0].shouldValidate).toBe(false)
    })

    it('sets shouldValidate based on touched state for description', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = { description: true }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )

      expect(rules[1].shouldValidate).toBe(true)
    })

    it('sets shouldValidate based on touched state for startedAt', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = { startedAt: true }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )

      expect(rules[2].shouldValidate).toBe(true)
    })

    it('sets shouldValidate true for endedAt when touched', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = { endedAt: true }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )

      expect(rules[3].shouldValidate).toBe(true)
    })

    it('sets shouldValidate true for endedAt when startedAt is touched and endedAt has value', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = { startedAt: true }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )

      expect(rules[3].shouldValidate).toBe(true)
    })

    it('sets shouldValidate false for endedAt when startedAt is touched but endedAt is empty', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '',
      }
      const touched = { startedAt: true }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )

      expect(rules[3].shouldValidate).toBe(false)
    })

    it('uses default false when touched fields are undefined', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = {}

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )

      expect(rules[0].shouldValidate).toBe(false)
      expect(rules[1].shouldValidate).toBe(false)
      expect(rules[2].shouldValidate).toBe(false)
      // endedAt: (touched.endedAt ?? false) || (touched.startedAt && !!formData.endedAt)
      // = (undefined ?? false) || (undefined && true) = false || false = false
      expect(rules[3].shouldValidate).toBeFalsy()
    })

    it('validator for name calls validateNameLocal with formData.name', () => {
      const formData = {
        name: 'Test Name',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = { name: true }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )
      rules[0].validator()

      expect(mockValidateName).toHaveBeenCalledWith('Test Name')
    })

    it('validator for description calls validateDescription', () => {
      const formData = {
        name: 'Test',
        description: '',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = { description: true }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )
      const result = rules[1].validator()

      expect(result).toBe('Description is required')
    })

    it('validator for startedAt calls validateStartDate', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '',
        endedAt: '2024-12-31',
      }
      const touched = { startedAt: true }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )
      const result = rules[2].validator()

      expect(result).toBe('Start date is required')
    })

    it('validator for endedAt calls validateEndDateLocal', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = { endedAt: true }

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )
      rules[3].validator()

      expect(mockValidateEndDate).toHaveBeenCalledWith('2024-12-31')
    })

    it('returns correct field names for each rule', () => {
      const formData = {
        name: 'Test',
        description: 'Description',
        startedAt: '2024-01-01',
        endedAt: '2024-12-31',
      }
      const touched = {}

      const rules = getCommonValidationRules(
        formData,
        touched,
        mockValidateName,
        mockValidateEndDate
      )

      expect(rules[0].field).toBe('name')
      expect(rules[1].field).toBe('description')
      expect(rules[2].field).toBe('startedAt')
      expect(rules[3].field).toBe('endedAt')
    })
  })
})
