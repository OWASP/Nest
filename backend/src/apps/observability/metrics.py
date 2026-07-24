"""Reusable Otel metrics for background jobs."""

import functools
import time

from opentelemetry import metrics

_meter = metrics.get_meter("nest.jobs")
_job_runs = _meter.create_counter(
    "nest.job.runs",
    description="Number of background job executions by status.",
)
_job_duration = _meter.create_histogram(
    "nest.job.duration",
    unit="s",
    description="Background job execution duration in seconds.",
)


def track_job(name, queue="default"):
    """Record run count and duration metrics for a background job.

    Wraps a callable so each execution increments ``nest.job.runs`` (labelled by
    job, queue and status) and records ``nest.job.duration``. The wrapped
    exception, if any, still propagates.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            status = "failure"
            try:
                result = func(*args, **kwargs)
                status = "success"
            finally:
                attributes = {"job": name, "queue": queue}
                _job_runs.add(1, {**attributes, "status": status})
                _job_duration.record(time.perf_counter() - start, attributes)
            return result

        return wrapper

    return decorator
