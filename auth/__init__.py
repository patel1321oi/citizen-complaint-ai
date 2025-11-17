# CitiZen AI Authentication Package
# This file makes the auth directory a Python package

__version__ = "1.0.0"
__author__ = "CitiZen AI Development Team"

# Import main authentication functions for easy access
from .user_auth import show_user_auth, create_user, authenticate_user
from .agent_auth import show_agent_auth, create_agent, authenticate_agent

__all__ = [
    'show_user_auth',
    'create_user', 
    'authenticate_user',
    'show_agent_auth',
    'create_agent',
    'authenticate_agent'
]