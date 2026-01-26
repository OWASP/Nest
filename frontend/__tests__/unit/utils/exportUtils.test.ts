import {
    buildExportQuery,
    downloadFile,
    getExportErrorMessage,
    parseExportResponse,
} from 'utils/exportUtils'

// Mock window APIs for download testing
const mockCreateObjectURL = jest.fn(() => 'blob:mock-url')
const mockRevokeObjectURL = jest.fn()
const mockAppendChild = jest.fn()
const mockRemoveChild = jest.fn()
const mockClick = jest.fn()

beforeEach(() => {
    jest.clearAllMocks()
    global.URL.createObjectURL = mockCreateObjectURL
    global.URL.revokeObjectURL = mockRevokeObjectURL
    document.body.appendChild = mockAppendChild
    document.body.removeChild = mockRemoveChild
})

describe('buildExportQuery', () => {
    it('should build query with CSV format', () => {
        const query = buildExportQuery({
            programKey: 'program-1',
            moduleKey: 'module-1',
            format: 'CSV',
        })

        expect(query).toContain('programKey: "program-1"')
        expect(query).toContain('moduleKey: "module-1"')
        expect(query).toContain('format: CSV')
        expect(query).not.toContain('label:')
    })

    it('should build query with JSON format and label', () => {
        const query = buildExportQuery({
            programKey: 'program-1',
            moduleKey: 'module-1',
            format: 'JSON',
            label: 'bug',
        })

        expect(query).toContain('format: JSON')
        expect(query).toContain('label: "bug"')
    })

    it('should skip label if value is "all"', () => {
        const query = buildExportQuery({
            programKey: 'p',
            moduleKey: 'm',
            format: 'CSV',
            label: 'all',
        })

        expect(query).not.toContain('label:')
    })
})

describe('parseExportResponse', () => {
    it('should extract export result from valid response', () => {
        const data = {
            getModule: {
                exportIssues: {
                    content: 'csv-content',
                    filename: 'export.csv',
                    mimeType: 'text/csv',
                    count: 10,
                },
            },
        }

        const result = parseExportResponse(data)

        expect(result).toEqual({
            content: 'csv-content',
            filename: 'export.csv',
            mimeType: 'text/csv',
            count: 10,
        })
    })

    it('should return null for invalid response', () => {
        expect(parseExportResponse(null)).toBeNull()
        expect(parseExportResponse({})).toBeNull()
        expect(parseExportResponse({ getModule: null })).toBeNull()
        expect(parseExportResponse({ getModule: {} })).toBeNull()
    })
})

describe('getExportErrorMessage', () => {
    it('should return error message for Error instance', () => {
        const error = new Error('Test error')
        expect(getExportErrorMessage(error)).toBe('Test error')
    })

    it('should return network error message', () => {
        const error = new Error('network failed')
        expect(getExportErrorMessage(error)).toContain('Network error')
    })

    it('should return timeout error message', () => {
        const error = new Error('request timeout')
        expect(getExportErrorMessage(error)).toContain('timed out')
    })

    it('should return default message for unknown error', () => {
        expect(getExportErrorMessage('unknown')).toContain('unexpected error')
    })
})

describe('downloadFile', () => {
    it('should create blob and trigger download', () => {
        const mockLink = {
            href: '',
            download: '',
            click: mockClick,
        }
        jest.spyOn(document, 'createElement').mockReturnValue(mockLink as any)

        downloadFile('test-content', 'test.csv', 'text/csv')

        expect(mockCreateObjectURL).toHaveBeenCalled()
        expect(mockLink.download).toBe('test.csv')
        expect(mockClick).toHaveBeenCalled()
        expect(mockRevokeObjectURL).toHaveBeenCalled()
    })
})
