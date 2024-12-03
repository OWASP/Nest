import { FontAwesomeIcon, FontAwesomeIconProps } from '@fortawesome/react-fontawesome'

type IconProp = FontAwesomeIconProps['icon']

interface MyIconProps extends Omit<FontAwesomeIconProps, 'icon'> {
  icon: string
}

const FontAwesomeIconWrapper = ({ icon, ...props }: MyIconProps) => (
  <FontAwesomeIcon icon={icon as IconProp} {...props} />
)

export default FontAwesomeIconWrapper
