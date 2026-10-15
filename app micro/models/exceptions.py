"""
models/exceptions.py
Custom exception hierarchy for the Weather Forecast Dashboard application.
Demonstrates robust Exception Handling in Python OOP.
"""

class WeatherAppException(Exception):
    """Base exception for all weather application errors."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}] {self.message}"


class InvalidInputError(WeatherAppException):
    """Raised when user input fails validation (e.g. empty city, illegal characters)."""
    def __init__(self, message: str = "Invalid city name entered. Please provide a valid location."):
        super().__init__(message, status_code=422)


class CityNotFoundError(WeatherAppException):
    """Raised when the requested city cannot be found in the API database."""
    def __init__(self, city: str):
        super().__init__(f"City '{city}' not found. Please verify spelling and country code.", status_code=404)
        self.city = city


class APIKeyError(WeatherAppException):
    """Raised when the OpenWeatherMap API key is missing, unauthorized, or expired."""
    def __init__(self, message: str = "Invalid or unauthorized API key. Please check your configuration."):
        super().__init__(message, status_code=401)


class NetworkConnectionError(WeatherAppException):
    """Raised when there is no internet connection or the server request times out."""
    def __init__(self, message: str = "Network connection failed. Please check your internet connectivity."):
        super().__init__(message, status_code=503)


class StorageError(WeatherAppException):
    """Raised when database or JSON file operations fail."""
    def __init__(self, message: str = "Failed to access or persist storage data."):
        super().__init__(message, status_code=500)
