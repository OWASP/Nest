import { faCode, faTags, faChartPie } from '@fortawesome/free-solid-svg-icons'
import ToggleableList from 'components/ToggleableList'
import AnchorTitle from 'components/AnchorTitle'

interface ListsSectionProps {
  languages?: string[]
  topics?: string[]
  tags?: string[]
  domains?: string[]
  type: string
}

const ListsSection = ({ languages, topics, tags, domains, type }: ListsSectionProps) => (
  <>
    {(type === 'project' || type === 'repository') && (
      <div
        className={`mb-8 grid grid-cols-1 gap-6 ${topics.length === 0 || languages.length === 0 ? 'md:col-span-1' : 'md:grid-cols-2'}`}
      >
        {languages.length !== 0 && (
          <ToggleableList
            items={languages}
            icon={faCode}
            label={<AnchorTitle title="Languages" />}
          />
        )}
        {topics.length !== 0 && (
          <ToggleableList items={topics} icon={faTags} label={<AnchorTitle title="Topics" />} />
        )}
      </div>
    )}
    {(type === 'program' || type === 'module') && (
      <div
        className={`mb-8 grid grid-cols-1 gap-6 ${(tags?.length || 0) === 0 || (domains?.length || 0) === 0 ? 'md:col-span-1' : 'md:grid-cols-2'}`}
      >
        {tags?.length > 0 && (
          <ToggleableList
            items={tags}
            icon={faTags}
            label={<AnchorTitle title="Tags" />}
            isDisabled={true}
          />
        )}
        {domains?.length > 0 && (
          <ToggleableList
            items={domains}
            icon={faChartPie}
            label={<AnchorTitle title="Domains" />}
            isDisabled={true}
          />
        )}
      </div>
    )}
  </>
)

export default ListsSection;
