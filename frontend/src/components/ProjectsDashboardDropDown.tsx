import { IconProp } from '@fortawesome/fontawesome-svg-core'
import { faArrowDownWideShort, faArrowUpShortWide } from '@fortawesome/free-solid-svg-icons'
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
  selectedLabels?: string[]
  selectionMode: 'single' | 'multiple'
  icon?: IconProp
  isOrdering?: boolean
  buttonDisplayName: string
  sections: DropDownSectionProps[]
}> = ({
  onAction,
  selectedKeys,
  selectionMode,
  icon,
  isOrdering,
  buttonDisplayName,
  sections,
  selectedLabels,
}) => {
  const orderingIconsMapping = {
    desc: faArrowDownWideShort,
    asc: faArrowUpShortWide,
  }
  return (
    <Dropdown>
      <DropdownTrigger>
        <Button variant="solid">
          <FontAwesomeIcon icon={isOrdering ? orderingIconsMapping[selectedKeys[0]] : icon} />
          <div className="flex flex-col items-center">
            <span className="text-md">{buttonDisplayName}</span>
            {selectedLabels && selectedLabels.length > 0 && (
              <span className="text-xs text-gray-500">{selectedLabels.join(', ')}</span>
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
