'use client'

import { faFileArrowDown } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { Tooltip } from '@heroui/tooltip'
import { FC } from 'react'
import { fetchMetricsPDF } from 'server/fetchMetricsPDF'

const MetricsPDFButton: FC<{
  path: string
  fileName: string
}> = ({ path, fileName }) => {
  return (
    <Tooltip
      content="Download as PDF"
      className="ml-2"
      placement="top"
      delay={100}
      closeDelay={100}
      showArrow
    >
      <button
        type="button"
        onClick={async () => await fetchMetricsPDF(path, fileName)}
        className="ml-2 cursor-pointer text-gray-500 transition-colors duration-200 hover:text-gray-700"
        aria-label="Download metrics as PDF"
      >
      <FontAwesomeIcon
        icon={faFileArrowDown}
        className="h-7 w-7"
        aria-hidden="true"
        />
      </button>
    </Tooltip>
  )
}

export default MetricsPDFButton
