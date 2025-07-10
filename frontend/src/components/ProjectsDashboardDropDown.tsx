import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  Dropdown,
  DropdownItem,
  DropdownTrigger,
  DropdownMenu,
  DropdownSection,
  Button,
} from '@heroui/react'

import { FC } from 'react'
import { DropDownSectionProps } from 'types/DropDownSectionProps'
const ProjectsDashboardDropDown: FC<{
  onAction: (key: string) => Promise<void>
  selectedKeys?: string[]
  selectionMode: 'single' | 'multiple'
  icon: IconProp
  buttonDisplayName: string
  sections: DropDownSectionProps[]
}> = ({ onAction, selectedKeys, selectionMode, icon, buttonDisplayName, sections }) => {
  return (
    <Dropdown>
      <DropdownTrigger>
        <Button variant="solid" color="success" className="text-white">
          <FontAwesomeIcon icon={icon} />
          {buttonDisplayName}
        </Button>
      </DropdownTrigger>
      <DropdownMenu onAction={onAction} selectedKeys={selectedKeys} selectionMode={selectionMode}>
        {sections.map((section) => (
          <DropdownSection key={section.title} title={section.title}>
            {section.items.map((item) => (
              <DropdownItem key={item.key}>{item.label}</DropdownItem>
            ))}
          </DropdownSection>
        ))}
      </DropdownMenu>
    </Dropdown>
  )
}

export default ProjectsDashboardDropDown
