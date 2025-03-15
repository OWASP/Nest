import { Tooltip } from 'components/ui/tooltip'

export const TruncatedText = ({
  text,
  maxLength = 40,
  className = '',
  disabledTooltip = false,
}: {
  text: string
  maxLength?: number
  className?: string
  disabledTooltip?: boolean
}) => {
  const isTruncated = text.length > maxLength && !disabledTooltip
  const displayText = isTruncated ? `${text.slice(0, maxLength)}...` : text

  return disabledTooltip ? (
    <span className={className}>{text}</span>
  ) : (
    <Tooltip content={text}>
      <span className={`truncate ${className}`}>{displayText}</span>
    </Tooltip>
  )
}
