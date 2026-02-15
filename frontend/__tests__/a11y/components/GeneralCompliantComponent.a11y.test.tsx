import { render } from '@testing-library/react'
import { axe } from 'jest-axe'
import { useTheme } from 'next-themes'
import { IconType } from 'react-icons'
import { FaCertificate } from 'react-icons/fa6'
import GeneralCompliantComponent from 'components/GeneralCompliantComponent'

type GeneralCompliantComponentProps = {
  compliant: boolean
  icon: IconType
  title: string
}

const baseProps: GeneralCompliantComponentProps = {
  compliant: true,
  icon: FaCertificate,
  title: 'Test Title',
}

describe.each([
  { theme: 'light', name: 'light' },
  { theme: 'dark', name: 'dark' },
])('GeneralCompliantComponent Accessibility ($name theme)', ({ theme }) => {
  beforeEach(() => {
    ;(useTheme as jest.Mock).mockReturnValue({ theme, setTheme: jest.fn() })
  })
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(<GeneralCompliantComponent {...baseProps} />)

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
