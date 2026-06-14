"""Custom exception classes for the OWASP application."""


class SnapshotProcessingError(Exception):
    """Exception raised for errors in snapshot processing."""


class CertificateIssuanceError(Exception):
    """Exception raised for errors in certificate issuance."""


class CertificateBatchIssuanceError(Exception):
    """Exception raised when one or more certificates fail in batch recalculation."""
