# CitiZen AI Machine Learning Package
# This file makes the ml directory a Python package

__version__ = "1.0.0"
__author__ = "CitiZen AI Development Team"

# Import main ML functions for easy access
from .model import (
    predict_urgency,
    predict_resolution_time,
    train_model_if_needed,
    get_model_info,
    test_model
)

__all__ = [
    'predict_urgency',
    'predict_resolution_time', 
    'train_model_if_needed',
    'get_model_info',
    'test_model'
]