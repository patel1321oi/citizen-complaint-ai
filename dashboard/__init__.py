# CitiZen AI Dashboard Package
# This file makes the dashboard directory a Python package

__version__ = "1.0.0"
__author__ = "CitiZen AI Development Team"

# Import main dashboard functions for easy access
from .user_dashboard import show_user_dashboard
from .agent_dashboard import show_agent_dashboard

__all__ = [
    'show_user_dashboard',
    'show_agent_dashboard'
]