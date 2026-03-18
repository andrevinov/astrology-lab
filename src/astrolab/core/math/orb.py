"""
Orb calculation utilities.

This module defines allowed orb values for different aspect types.
All values are deterministic and configurable in one place.
"""

from typing import Dict

# Default orb values in degrees
DEFAULT_ORBS: Dict[str, float] = {
    "conjunction": 8.0,
    "opposition": 8.0,
    "trine": 6.0,
    "square": 6.0,
    "sextile": 4.0,
}


def get_orb(aspect_type: str) -> float:
    """
    Return the allowed orb (in degrees) for a given aspect type.

    Parameters
    ----------
    aspect_type : str
        Name of the aspect (e.g., 'conjunction', 'opposition').

    Returns
    -------
    float
        Orb in degrees.

    Raises
    ------
    ValueError
        If the aspect type is unknown.
    """
    try:
        return DEFAULT_ORBS[aspect_type]
    except KeyError:
        raise ValueError(f"Unknown aspect type: {aspect_type}")