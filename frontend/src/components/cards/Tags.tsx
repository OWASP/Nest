import { FaCode, FaTags, FaChartPie } from 'react-icons/fa6'
import AnchorTitle from 'components/AnchorTitle'
import ToggleableList from 'components/ToggleableList'

interface TagsProps {
  entityKey?: string
  languages?: string[]
  topics?: string[]
  tags?: string[]
  domains?: string[]
  labels?: string[]
}

const Tags = ({ entityKey, languages, topics, tags, domains, labels }: TagsProps) => {
  const hasLanguagesOrTopics = (languages?.length || 0) > 0 || (topics?.length || 0) > 0

  const tagSections = [
    { icon: FaTags, items: tags, name: 'tags', title: 'Tags' },
    { icon: FaChartPie, items: domains, name: 'domains', title: 'Domains' },
    { icon: FaTags, items: labels, name: 'labels', title: 'Labels' },
  ].filter((section) => (section.items?.length || 0) > 0)

  const fullWidthIndex = tagSections.length % 2 === 1 ? tagSections.length - 1 : -1

  // Languages and Topics section
  if (hasLanguagesOrTopics) {
    return (
      <div
        className={`mb-8 grid grid-cols-1 gap-6 ${(topics?.length ?? 0) === 0 || (languages?.length ?? 0) === 0 ? 'md:col-span-1' : 'md:grid-cols-2'}`}
      >
        {languages && languages.length !== 0 && (
          <ToggleableList
            entityKey={`${entityKey}-languages`}
            items={languages}
            icon={FaCode}
            label={<AnchorTitle title="Languages" />}
          />
        )}
        {topics && topics.length !== 0 && (
          <ToggleableList
            entityKey={`${entityKey}-topics`}
            items={topics}
            icon={FaTags}
            label={<AnchorTitle title="Topics" />}
          />
        )}
      </div>
    )
  }

  // Tags, Domains, and Labels section
  if (tagSections.length > 0) {
    return (
      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-2">
        {tagSections.map((section, index) => (
          <ToggleableList
            key={section.name}
            entityKey={`${entityKey}-${section.name}`}
            items={section.items ?? []}
            icon={section.icon}
            label={<AnchorTitle title={section.title} />}
            isDisabled={true}
            className={index === fullWidthIndex ? 'md:col-span-2' : ''}
          />
        ))}
      </div>
    )
  }

  return null
}

export default Tags
