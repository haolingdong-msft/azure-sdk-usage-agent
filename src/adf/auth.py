"""
Authentication utilities for Azure Data Factory.
"""

from typing import Optional
from azure.identity import DefaultAzureCredential

from .config import MANAGEMENT_SCOPE


def get_token(credential: Optional[DefaultAzureCredential] = None) -> str:
    """
    Get an Azure access token for Azure Management API.
    
    Args:
        credential: Azure credential instance. If None, creates a new DefaultAzureCredential.
    
    Returns:
        str: Bearer token for authentication
    """
    if credential is None:
        credential = DefaultAzureCredential()
    
    token = credential.get_token(MANAGEMENT_SCOPE)
    return token.token
