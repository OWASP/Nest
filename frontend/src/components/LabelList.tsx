import React from 'react'

interface LabelProps {
  label: string
  className?: string
}

const Label: React.FC<LabelProps> = ({ label, className = '' }) => {
  return (
    <span
      className={`flex items-center justify-center gap-2 rounded-md border border-zinc-800 bg-transparent px-3 py-2 text-xs text-zinc-800 transition-all hover:bg-zinc-500 hover:text-white dark:border-white dark:text-white dark:hover:bg-white dark:hover:text-black ${className}`}
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
