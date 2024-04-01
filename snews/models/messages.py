# -*- coding: utf-8 -*-
__all__ = [
    "HeartBeat",
    "Retraction",
    "CoincidenceTierMessage",
    "SignificanceTierMessage",
    "TimingTierMessage"
]

# Standard library modules
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4

# Third-party modules
import numpy as np
from pydantic import (UUID4, BaseModel, Field, NonNegativeFloat,
                      field_validator, model_validator, root_validator,
                      validator)

# Local modules
from ..__version__ import schema_version
from ..data import detectors
from ..models.timing import PrecisionTimestamp


# .................................................................................................
def convert_timestamp_to_ns_precision(timestamp: Union[str, datetime, np.datetime64]) -> str:
    """
    Convert timestamp to nanosecond precision

    Parameters
    ---------
    timestamp : Union[str, datetime, np.datetime64]
    Timestamp in any format supported by numpy.datetime64

    Returns
    -------
    str
    Timestamp at nanosecond precision in ISO 8601-1:2019 format
    """

    return PrecisionTimestamp(timestamp=timestamp, precision="ns").to_string()


# .................................................................................................
class Tier(str, Enum):
    HEART_BEAT = "Heartbeat"
    RETRACTION = "Retraction"
    TIMING_TIER = "TimingTier"
    SIGNIFICANCE_TIER = "SignificanceTier"
    COINCIDENCE_TIER = "CoincidenceTier"


# .................................................................................................
class MessageBase(BaseModel):
    """
    Base class for all messages.
    """

    class Config:
        validate_assignment = True

    id: Optional[str] = Field(
        default=None,
        title="Human-readable message ID",
        description="Textual identifier for the message"
    )

    uid: UUID4 = Field(
        title="Unique message ID",
        default_factory=uuid4,
        description="Unique identifier for the message"
    )

    tier: Tier = Field(
        ...,
        title="Message Tier",
        description="Message tier",
    )

    sent_time_utc: Optional[str] = Field(
        default=None,
        title="Sent time (UTC)",
        description="Time the message was sent in ISO 8601-1:2019 format"
    )

    machine_time_utc: Optional[str] = Field(
        default=None,
        title="Machine time (UTC)",
        description="Time of the event at the detector in ISO 8601-1:2019 format"
    )

    is_pre_sn: Optional[bool] = Field(
        default=False,
        title="Pre-SN Flag",
        description="True if the message is associated with pre-SN"
    )

    is_test: Optional[bool] = Field(
        default=False,
        title="Test Flag",
        description="True if the message is a test"
    )

    is_firedrill: Optional[bool] = Field(
        default=False,
        title="Fire Drill Flag",
        description="True if the message is associated with a fire drill"
    )

    meta: Optional[dict] = Field(
        default=None,
        title="Metadata",
        description="Attached metadata"
    )

    schema_version: Optional[str] = Field(
        default=schema_version,
        title="Schema Version",
        description="Schema version of the message",
        frozen=True,
    )

    @validator("sent_time_utc", "machine_time_utc", pre=True, always=True)
    def _convert_timestamp_to_ns_precision(cls, v):
        """
        Convert to nanosecond precision (before running Pydantic validators).
        """
        if v is not None:
            return convert_timestamp_to_ns_precision(timestamp=v)

    @model_validator(mode="after")
    def _format_id(self):
        """
        Validate the full model.
        """

        # If id is not set, generate one based on detector name, tier, and machine time
        if self.id is None:
            self.id = f"{self.detector_name}_{self.tier.value}_{self.machine_time_utc}"

        return self


# .................................................................................................
class DetectorMessageBase(MessageBase):
    """
    Base class for all messages related to a specific detector.
    """

    class Config:
        validate_assignment = True

    detector_name: str = Field(
        ...,
        title="Detector Name",
        description="Name of the detector that sent the message"
    )

    @model_validator(mode="after")
    def _validate_detector_name(self) -> str:
        """
        Ensure the detector name is in the list of supported detectors.
        """

        if self.detector_name not in detectors.names and not self.is_test:
            raise ValueError(f"Invalid detector name. Options are: {detectors.names}")
        return self


# .................................................................................................
class HeartBeat(DetectorMessageBase):
    """
    Heartbeat detector message.
    """

    class Config:
        validate_assignment = True

    detector_status: str = Field(
        ...,
        title="Detector Status",
        description="Status of the detector",
        examples=["ON", "OFF"]
    )

    @root_validator(pre=True)
    def _set_tier(cls, values):
        values['tier'] = Tier.HEART_BEAT
        return values

    @field_validator("detector_status")
    def _validate_detector_status(cls, v):
        if v not in {"ON", "OFF"}:
            raise ValueError("Detector status must be either ON or OFF")
        return v

    @model_validator(mode="after")
    def _validate_model(self):
        # Model-wide validataion after initiation goes here
        return self


# .................................................................................................
class Retraction(DetectorMessageBase):
    """
    Retraction detector message.
    """

    class Config:
        validate_assignment = True

    retract_message_uid: Optional[UUID4] = Field(
        default=None,
        title="Unique message ID",
        description="Unique identifier for the message to retract"
    )

    retract_latest: bool = Field(
        default=False,
        title="Retract Latest Flag",
        description="True if the latest message is being retracted",
    )

    retraction_reason: str = Field(
        ...,
        title="Retraction reason",
        description="Reason for retraction",
    )

    @root_validator(pre=True)
    def _set_tier(cls, values):
        values['tier'] = Tier.RETRACTION
        return values

    @model_validator(mode="after")
    def _validate_model(self):
        if self.retract_latest and self.retract_message_uid is not None:
            raise ValueError("retract_message_uid cannot be specified when retract_latest=True")

        if not self.retract_latest and self.retract_message_uid is None:
            raise ValueError("Must specify either retract_message_uid or retract_latest=True")
        return self


# .................................................................................................
class TierMessageBase(DetectorMessageBase):
    """
    Tier detector base message
    """

    class Config:
        validate_assignment = True

    p_val: Optional[NonNegativeFloat] = Field(
        default=None,
        title="P-value",
        description="p-value of coincidence",
        le=1,
    )

    @model_validator(mode="after")
    def validate_model(self):
        # Model-wide validataion after initiation goes here
        return self


# .................................................................................................
class TimingTierMessage(TierMessageBase):
    """
    Timing tier detector message.
    """

    class Config:
        validate_assignment = True

    timing_series: List[str] = Field(
        ...,
        title="Timing Series",
        description="Timing series of the event",
    )

    @root_validator(pre=True)
    def _set_tier(cls, values):
        values['tier'] = Tier.TIMING_TIER
        return values

    @field_validator("timing_series")
    def _validate_timing_series(cls, v: List[str]):
        try:
            converted_timestamps = list(map(convert_timestamp_to_ns_precision, v))
        except ValueError:
            raise ValueError("Timing series entries must be in ISO 8601-1:2019 format")
        return converted_timestamps

    @model_validator(mode="after")
    def _validate_model(self):
        # Model-wide validataion after initiation goes here
        return self


# .................................................................................................
class SignificanceTierMessage(TierMessageBase):
    """
    Significance tier detector message.
    """

    class Config:
        validate_assignment = True

    p_values: List[NonNegativeFloat] = Field(
        ...,
        title="p-values",
        description="p-values for the event",
    )

    t_bin_width_sec: NonNegativeFloat = Field(
        ...,
        title="Time Bin Width (s)",
        description="Time bin width of the event",
    )

    @root_validator(pre=True)
    def _set_tier(cls, values):
        values['tier'] = Tier.SIGNIFICANCE_TIER
        return values

    @field_validator("p_values")
    def _validate_p_values(cls, v):
        if any(p > 1 for p in v):
            raise ValueError("p-value in list out of range.")
        return v

    @field_validator("t_bin_width_sec")
    def _validate_t_bin_width(cls, v):
        return v

    @model_validator(mode="after")
    def _validate_model(self):
        # Model-wide validataion after initiation goes here
        return self


# .................................................................................................
class CoincidenceTierMessage(TierMessageBase):
    """
    Coincidence tier detector message.
    """

    class Config:
        validate_assignment = True

    neutrino_time_utc: str = Field(
        ...,
        title="Neutrino Time (UTC)",
        description="Time of the first neutrino in the event in ISO 8601-1:2019 format"
    )

    @root_validator(pre=True)
    def _set_tier(cls, values):
        values['tier'] = Tier.COINCIDENCE_TIER
        return values

    @field_validator("neutrino_time_utc")
    def _validate_neutrino_time_format(cls, v: str):
        return convert_timestamp_to_ns_precision(v)

    @model_validator(mode="after")
    def _validate_neutrino_time(self):
        now = datetime.now(UTC)

        # Cast into ISO 8601-1:2019 format with ns precision
        neutrino_time_pt = PrecisionTimestamp(timestamp=self.neutrino_time_utc)

        if not self.is_test:
            # Check newer than 48 hours ago
            if neutrino_time_pt.to_datetime() < now - timedelta(hours=48):
                raise ValueError("neutrino_time_utc must be within past 48 hours")

            # Check not in the future
            if neutrino_time_pt.to_datetime() > now:
                raise ValueError("neutrino_time_utc must be in the past")

        return self
