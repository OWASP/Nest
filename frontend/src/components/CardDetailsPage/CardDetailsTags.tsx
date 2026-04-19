import { FaCode, FaTags, FaChartPie } from 'react-icons/fa6'
import AnchorTitle from 'components/AnchorTitle'
import ToggleableList from 'components/ToggleableList'

interface CardDetailsTagsProps {
  entityKey?: string
  languages?: string[]
  topics?: string[]
  tags?: string[]
  domains?: string[]
  labels?: string[]
}

const CardDetailsTags = ({
  entityKey,
  languages,
  topics,
  tags,
  domains,
  labels,
}: CardDetailsTagsProps) => {
  const hasLanguagesOrTopics = (languages?.length || 0) > 0 || (topics?.length || 0) > 0
  const hasTagsDomainsOrLabels =
    (tags?.length || 0) > 0 || (domains?.length || 0) > 0 || (labels?.length || 0) > 0

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
  if (hasTagsDomainsOrLabels) {
    return (
      <>
        {((tags?.length || 0) > 0 || (domains?.length || 0) > 0) && (
          <div
            className={`mb-8 grid grid-cols-1 gap-6 ${(tags?.length || 0) === 0 || (domains?.length || 0) === 0 ? 'md:col-span-1' : 'md:grid-cols-2'}`}
          >
            {tags && tags.length > 0 && (
              <ToggleableList
                entityKey={`${entityKey}-tags`}
                items={tags}
                icon={FaTags}
                label={<AnchorTitle title="Tags" />}
                isDisabled={true}
              />
            )}
            {domains && domains.length > 0 && (
              <ToggleableList
                entityKey={`${entityKey}-domains`}
                items={domains}
                icon={FaChartPie}
                label={<AnchorTitle title="Domains" />}
                isDisabled={true}
              />
            )}
          </div>
        )}
        {labels && labels.length > 0 && (
          <div className="mb-8">
            <ToggleableList
              entityKey={`${entityKey}-labels`}
              items={labels}
              icon={FaTags}
              label={<AnchorTitle title="Labels" />}
              isDisabled={true}
            />
          </div>
        )}
      </>
    )
  }

  return null
}

export default CardDetailsTags
