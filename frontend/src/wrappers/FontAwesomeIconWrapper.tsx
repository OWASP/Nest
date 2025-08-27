import { FontAwesomeIcon, FontAwesomeIconProps } from '@fortawesome/react-fontawesome'

type IconProp = FontAwesomeIconProps['icon']

interface MyIconProps extends Omit<FontAwesomeIconProps, 'icon'> {
  icon: string | IconProp
}

const FontAwesomeIconWrapper = ({ icon = 'fa-solid fa-medal', ...props }: MyIconProps) => {
  // For now, just use the default icon since we're not using string-based icons
  return <FontAwesomeIcon icon={icon as IconProp} {...props} />
}

export default FontAwesomeIconWrapper
