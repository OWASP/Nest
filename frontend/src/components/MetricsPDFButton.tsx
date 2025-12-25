'use client'

import { Tooltip } from '@heroui/tooltip'
import { FC } from 'react'
import { FaFileArrowDown } from 'react-icons/fa6'
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
      <FaFileArrowDown
        className="ml-2 h-7 w-7 cursor-pointer text-gray-500 transition-colors duration-200 hover:text-gray-700"
        onClick={async () => await fetchMetricsPDF(path, fileName)}
      />
    </Tooltip>
  )
}

export default MetricsPDFButton
