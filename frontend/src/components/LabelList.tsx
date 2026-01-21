import React from 'react'

interface LabelProps {
  label: string
  className?: string
}

const Label: React.FC<LabelProps> = ({ label, className = '' }) => {
  return (
    <span
      className={`inline-block rounded-lg border border-gray-400 px-2 py-0.5 text-xs text-gray-700 hover:bg-gray-200 dark:border-gray-300 dark:text-gray-300 dark:hover:bg-gray-700 ${className}`}
    >
      {label}
    </span>
  )
}

interface LabelListProps {
  entityKey: string
  labels: string[]
  maxVisible?: number
  className?: string
}

const LabelList: React.FC<LabelListProps> = ({
  entityKey,
  labels,
  maxVisible = 5,
  className = '',
}) => {
  if (!labels || labels.length === 0) return null

  const visibleLabels = labels.slice(0, maxVisible)
  const remainingCount = labels.length - maxVisible
  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {visibleLabels.map((label) => (
        <Label key={`${entityKey}-${label}`} label={label} />
      ))}
      {remainingCount > 0 && <Label label={`+${remainingCount} more`} />}
    </div>
  )
}

export { LabelList }
