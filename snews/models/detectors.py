# -*- coding: utf-8 -*-
__all__ = ["Detector", "DetectorType"]

# Standard library modules
from enum import Enum
from typing import Optional

# Third-party modules
from pydantic import (AnyHttpUrl, BaseModel, Field, NonNegativeFloat, PastDate,
                      model_validator)
from pydantic_extra_types.coordinate import Latitude, Longitude
from pydantic_extra_types.country import CountryAlpha2


# .................................................................................................
class DetectorType(Enum):
    WATER_CERENKOV = "Water Cerenkov"
    LIQUID_SCINTILLATOR = "Liquid Scintillator"
    LIQUID_ARGON = "Liquid Argon"
    BUBBLE_CHAMBER = "Bubble Chamber"
    HIGH_Z = "High-Z"
    OTHER = "Other"


# .................................................................................................
class Detector(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier for the detector"
    )

    name: str = Field(
        description="Common name of the detector"
    )

    name_full: str = Field(
        description="Full name of the detector",
    )

    type: DetectorType = Field(
        description="Type of detector",
    )

    experiment: str = Field(
        description="Name of neutrino experiment",
    )

    mass_kt: NonNegativeFloat = Field(
        description="Detector mass",
    )

    depth_meters: NonNegativeFloat = Field(
        description="Detector depth in meters",
    )

    depth_mwe: NonNegativeFloat = Field(
        description="Detector depth in meters-water-equivalent",
    )

    facility: str = Field(
        description="Name of facility where detector is located",
    )

    latitude: Latitude = Field(
        description="Latitude of detector",
    )

    longitude: Longitude = Field(
        description="Longitude of detector",
    )

    city: Optional[str] = Field(
        default=None,
        description="City where detector is located",
    )

    region: Optional[str] = Field(
        default=None,
        description="State/province/region where detector is located",
    )

    country: CountryAlpha2 = Field(
        description="Country where detector is located",
    )

    website: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Experiment website",
    )

    logo: Optional[AnyHttpUrl] = Field(
        default=None,
        description="Experiment logo",
    )

    snews_member_status: bool = Field(
        default=False,
        description="Whether detector is a member of SNEWS",
    )

    snews_member_since: Optional[PastDate] = Field(
        default=None,
        description="Date when detector joined SNEWS",
    )

    @model_validator(mode="after")
    def validate_model(cls, values):
        # Any model-wide validation should go here
        return values

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Detector):
            return False

        return self.model_dump() == other.model_dump()


def __dir__() -> list[str]:
    return __all__
