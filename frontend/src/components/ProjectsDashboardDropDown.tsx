import {
  Dropdown,
  DropdownItem,
  DropdownTrigger,
  DropdownMenu,
  DropdownSection,
  Header,
} from '@heroui/react'
import type { Key } from 'react'

import { FC } from 'react'
import type { IconType } from 'react-icons'
import { FaArrowDownWideShort, FaArrowUpShortWide } from 'react-icons/fa6'
import { IconWrapper } from 'wrappers/IconWrapper'
import { DropDownSectionProps } from 'types/DropDownSectionProps'

const ProjectsDashboardDropDown: FC<{
  onAction: (key: Key) => void
  selectedKeys?: string[]
  selectedLabels?: string[]
  selectionMode: 'single' | 'multiple'
  icon?: IconType
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
    desc: FaArrowDownWideShort,
    asc: FaArrowUpShortWide,
  }

  return (
    <Dropdown>
      <DropdownTrigger>
        <div role="button" tabIndex={0} className="flex cursor-pointer items-center gap-2">
          <IconWrapper
            icon={
              isOrdering
                ? orderingIconsMapping[selectedKeys?.[0] as keyof typeof orderingIconsMapping] ||
                  FaArrowDownWideShort
                : icon || FaArrowDownWideShort
            }
          />
          <div className="flex flex-col items-center">
            <span className="text-md">{buttonDisplayName}</span>
            {selectedLabels && selectedLabels.length > 0 && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {selectedLabels.join(', ')}
              </span>
            )}
          </div>
        </div>
      </DropdownTrigger>
      <DropdownMenu onAction={onAction} selectedKeys={selectedKeys} selectionMode={selectionMode}>
        {sections.map((section) => (
          <DropdownSection key={section.title} aria-label={section.title}>
            <Header>{section.title}</Header>
            {section.items.map((item) => (
              <DropdownItem key={item.key} id={item.key} textValue={item.label}>
                {item.label}
              </DropdownItem>
            ))}
          </DropdownSection>
        ))}
      </DropdownMenu>
    </Dropdown>
  )
}

export default ProjectsDashboardDropDown
