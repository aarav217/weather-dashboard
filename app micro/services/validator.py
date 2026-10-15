"""
services/validator.py
Input validation module for Weather Forecast Dashboard.
"""

import re
from models.exceptions import InvalidInputError


class InputValidator:
    """
    Validates and sanitizes city queries entered by the user.
    """

    # Matches letters, spaces, commas, hyphens, and apostrophes (e.g., 'New York', 'Saint-Louis', 'Bengaluru, IN')
    _VALID_CITY_REGEX = re.compile(r"^[A-Za-z\s\.\-,\'\u00C0-\u024F]+$")

    @classmethod
    def validate_city(cls, city: str) -> str:
        """
        Validates the city input string.
        Returns the sanitized, cleaned city string.
        Raises InvalidInputError if invalid.
        """
        if city is None:
            raise InvalidInputError("City name cannot be empty. Please enter a city.")

        cleaned = city.strip()
        if not cleaned:
            raise InvalidInputError("City name cannot be blank. Please enter a valid city name.")

        if len(cleaned) < 2:
            raise InvalidInputError("City name is too short. Please enter at least 2 characters.")

        if len(cleaned) > 80:
            raise InvalidInputError("City name is too long. Please enter a valid name under 80 characters.")

        if not cls._VALID_CITY_REGEX.match(cleaned):
            raise InvalidInputError(
                f"City name '{cleaned}' contains invalid characters. Use letters, spaces, or commas."
            )

        # Remove duplicate spaces and clean around commas
        parts = [p.strip() for p in cleaned.split(",") if p.strip()]
        if len(parts) > 1:
            # City, CountryCode format
            return f"{parts[0].title()}, {parts[1].upper()}"
        return parts[0].title()
