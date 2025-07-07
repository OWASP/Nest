import Link from "next/link";
import { FC } from "react";
import { HealthMetricsProps } from "types/healthMetrics";

const MetricsCard: FC<{ metric: HealthMetricsProps }> = ({ metric }) => {
  return (
    <Link href={`/projects/dashboard/metrics/${metric.id}`} className="no-underline text-gray-800 dark:text-gray-200">
    <div className="grid grid-cols-8 p-4 bg-white dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200">
        <div className="col-span-3 truncate">
            <p className="text-md">{metric.projectName}</p>
        </div>
        <div className="col-span-1 truncate">
            <p className="text-md">{metric.score}</p>
        </div>
        <div className="col-span-1 truncate">
            <p className="text-md">{metric.starsCount}</p>
        </div>
        <div className="col-span-1 truncate">
            <p className="text-md">{metric.forksCount}</p>
        </div>
        <div className="col-span-1 truncate">
            <p className="text-md">{metric.contributorsCount}</p>
        </div>
        <div className="col-span-1 truncate">
            <p className="text-md">{new Date(metric.createdAt).toLocaleDateString()}</p>
        </div>
    </div>
    </Link>

  );
};

export default MetricsCard;
