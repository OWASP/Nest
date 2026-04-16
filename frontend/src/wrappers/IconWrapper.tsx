import { ComponentProps } from 'react'
import type { IconType } from 'react-icons'

export interface IconWrapperProps extends ComponentProps<'svg'> {
  icon: IconType
  size?: string | number
}

const IconWrapper = ({ icon: Icon, className, ...props }: IconWrapperProps) => (
  <Icon className={className} {...props} />
)

export { IconWrapper }
