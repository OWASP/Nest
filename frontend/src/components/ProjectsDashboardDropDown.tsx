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
  onAction: (key: string) => void
  selectedKeys?: string[]
  selectionMode: 'single' | 'multiple'
  icon: IconProp
  buttonDisplayName: string
  sections: DropDownSectionProps[]
  isOrdering?: boolean
}> = ({ onAction, selectedKeys, selectionMode, icon, buttonDisplayName, sections, isOrdering }) => {
  let displayKeys = selectedKeys || []
  if (isOrdering && selectedKeys && selectedKeys.length > 0) {
    displayKeys = selectedKeys.map((key) =>
      key.replace(/ASC/, ' ascending').replace(/DESC/, ' descending')
    )
  }
  return (
    <Dropdown>
      <DropdownTrigger>
        <Button variant="solid">
          <FontAwesomeIcon icon={icon} />
          <div className="flex flex-col items-center">
            <span className="text-md">{buttonDisplayName}</span>
            {selectedKeys && selectedKeys.length > 0 && (
              <span className="text-xs text-gray-500">{displayKeys.join(', ')}</span>
            )}
          </div>
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
