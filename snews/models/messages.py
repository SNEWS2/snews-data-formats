# -*- coding: utf-8 -*-

# Standard library modules
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4

# Third-party modules
import numpy as np
from pydantic import (BaseModel, Field, NonNegativeFloat, ValidationError,
                      field_validator, model_validator)

# Local modules
from ..__version__ import schema_version
from ..data import detectors
from ..models.timing import PrecisionTimestamp

__all__ = [
    "HeartbeatMessage",
    "RetractionMessage",
    "CoincidenceTierMessage",
    "SignificanceTierMessage",
    "TimingTierMessage",
    "compatible_message_types",
    "create_messages",
]


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

    uuid: str = Field(
        title="Unique message ID",
        default_factory=uuid4,
        description="Unique identifier for the message",
        validate_default=True
    )

    tier: Tier = Field(
        ...,
        title="Message Tier",
        description="Message tier",
    )

    sent_time_utc: Optional[str] = Field(
        default=None,
        title="Sent time (UTC)",
        description="Time the message was sent in ISO 8601-1:2019 format",
        validate_default=True
    )

    machine_time_utc: Optional[str] = Field(
        default=None,
        title="Machine time (UTC)",
        description="Time of the event at the detector in ISO 8601-1:2019 format",
        validate_default=True
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

    @field_validator("sent_time_utc", "machine_time_utc", mode="before")
    def _convert_timestamp_to_ns_precision(cls, v):
        """
        Convert to nanosecond precision (before running Pydantic validators).
        """
        if v is not None:
            return convert_timestamp_to_ns_precision(timestamp=v)

    @field_validator("uuid", mode="before")
    def _cast_uuid_to_string(cls, v):
        """
        Cast UUID to string (before running Pydantic validators).
        """
        return str(v)

    @model_validator(mode="after")
    def _format_id(self):
        """
        Validate the full model.
        """

        # If id is not set, generate one based on detector name, tier, and machine time
        if self.id is None:
            self.id = f"{self.detector_name}_{self.tier.value}_{self.machine_time_utc}"

        return self

    def fields(self):
        """
        Return a list of fields for the message.
        """
        return list(self.model_fields.keys())

    def required_fields(self):
        """
        Return a list of required fields for the message.
        """
        return [k for k, v in self.model_fields.items() if v.is_required()]


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
class HeartbeatMessage(DetectorMessageBase):
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

    @model_validator(mode="before")
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
class RetractionMessage(DetectorMessageBase):
    """
    Retraction detector message.
    """

    class Config:
        validate_assignment = True

    retract_message_uid: Optional[str] = Field(
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

    @model_validator(mode="before")
    def _set_tier(cls, values):
        values['tier'] = Tier.RETRACTION
        return values

    @model_validator(mode="after")
    def _validate_model(self):
        if self.retract_latest and self.retract_message_uid is not None:
            raise ValueError("retract_message_uuid cannot be specified when retract_latest=True")

        if not self.retract_latest and self.retract_message_uid is None:
            raise ValueError("Must specify either retract_message_uuid or retract_latest=True")
        return self


# .................................................................................................
class TierMessageBase(DetectorMessageBase):
    """
    Tier base message
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

    timing_series: List[Union[str, int]] = Field(
        ...,
        title="Timing Series",
        description="Timing series of the event",
    )

    @model_validator(mode="before")
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

    @model_validator(mode="before")
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

    @model_validator(mode="before")
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


# .................................................................................................
def compatible_message_types(**kwargs) -> list:
    """
    Return a list of message types that are compatible with the given keyword arguments.
    """

    message_types = [
        HeartbeatMessage,
        RetractionMessage,
        CoincidenceTierMessage,
        SignificanceTierMessage,
        TimingTierMessage,
    ]

    compatible_message_types = []
    for message_type in message_types:
        try:
            message_type(**kwargs)
            compatible_message_types.append(message_type)
        except ValidationError:
            pass

    return compatible_message_types


# .................................................................................................
def create_messages(**kwargs) -> list:
    """
    Return a list of messages initialized with the given keyword arguments.
    """

    messages = []
    for message_type in compatible_message_types(**kwargs):
        messages.append(message_type(**kwargs))

    return messages
