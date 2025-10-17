import { IS_PROJECT_HEALTH_ENABLED } from 'utils/env.client'
import HealthMetrics from 'components/HealthMetrics'
import type { HealthMetricsProps } from 'types/healthMetrics'

interface HealthSectionProps {
 healthMetricsData?: HealthMetricsProps[]
  type: string
}

const HealthSection = ({ healthMetricsData, type }: HealthSectionProps) =>
  IS_PROJECT_HEALTH_ENABLED &&
  type === 'project' &&
  healthMetricsData?.length > 0 && <HealthMetrics data={healthMetricsData} />

export default HealthSection;
