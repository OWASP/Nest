"""Tests for the track_job metrics helper."""

import pytest

from apps.observability.metrics import track_job

METRICS_PATH = "apps.observability.metrics"


class TestTrackJob:
    def test_records_success(self, mocker):
        runs = mocker.patch(f"{METRICS_PATH}._job_runs")
        duration = mocker.patch(f"{METRICS_PATH}._job_duration")

        @track_job("generate_ai_reply", queue="ai")
        def do_work(value):
            return value * 2

        result = do_work(5)

        assert result == 10
        runs.add.assert_called_once_with(
            1, {"job": "generate_ai_reply", "queue": "ai", "status": "success"}
        )
        assert duration.record.call_args.args[1] == {"job": "generate_ai_reply", "queue": "ai"}

    def test_records_failure_and_reraises(self, mocker):
        runs = mocker.patch(f"{METRICS_PATH}._job_runs")
        duration = mocker.patch(f"{METRICS_PATH}._job_duration")

        @track_job("generate_ai_reply", queue="ai")
        def do_work():
            message = "boom"
            raise ValueError(message)

        with pytest.raises(ValueError, match="boom"):
            do_work()

        runs.add.assert_called_once_with(
            1, {"job": "generate_ai_reply", "queue": "ai", "status": "failure"}
        )
        duration.record.assert_called_once()
        assert duration.record.call_args.args[1] == {"job": "generate_ai_reply", "queue": "ai"}

    def test_defaults_to_default_queue(self, mocker):
        runs = mocker.patch(f"{METRICS_PATH}._job_runs")
        mocker.patch(f"{METRICS_PATH}._job_duration")

        @track_job("some_job")
        def do_work():
            return None

        do_work()

        runs.add.assert_called_once_with(
            1, {"job": "some_job", "queue": "default", "status": "success"}
        )

    def test_preserves_wrapped_function_metadata(self):
        @track_job("some_job")
        def do_work():
            """Do some work."""

        assert do_work.__name__ == "do_work"
        assert do_work.__doc__ == "Do some work."
