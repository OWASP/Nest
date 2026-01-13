import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'
import { IconType } from 'react-icons'
import { FaCertificate } from 'react-icons/fa6'
import GeneralCompliantComponent from 'components/GeneralCompliantComponent'

expect.extend(toHaveNoViolations)

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

describe('GeneralCompliantComponent Accessibility', () => {
  it('should not have any accessibility violations', async () => {
    const { baseElement } = render(<GeneralCompliantComponent {...baseProps} />)

    const results = await axe(baseElement)

    expect(results).toHaveNoViolations()
  })
})
