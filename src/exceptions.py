"""Exceptions for business rules"""


class BusinessRuleError(Exception):
    """Error for business rule errors"""
    pass


class NotFoundError(Exception):
    """Error for object not found in storage"""
    pass


class DuplicateError(Exception):
    """Error for duplicate object(for example, duplicate IP)"""
    pass
