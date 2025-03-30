import { IconDefinition } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import millify from 'millify'
import React from 'react'

const InfoItem: React.FC<{
  icon: IconDefinition
  label: string
  precision?: number
  value: number
}> = ({ icon, label, precision = 1, value }) => {
  const formattedValue = millify(value, { precision: precision })

  return (
    <div className="flex items-center justify-between">
      <span className="flex items-center">
        <FontAwesomeIcon icon={icon} className="mr-2 h-4 w-4" />
        {label}
      </span>
      <span className="font-medium">{formattedValue}</span>
    </div>
  )
}

export default InfoItem
