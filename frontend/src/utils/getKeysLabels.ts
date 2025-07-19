import { DropDownSectionProps } from 'types/DropDownSectionProps'

export function getKeysLabels(sections: DropDownSectionProps[], selectedKeys: string[]): string[] {
  return sections
    .flatMap((section) => section.items)
    .filter((item) => selectedKeys.includes(item.key))
    .map((item) => item.label)
}
