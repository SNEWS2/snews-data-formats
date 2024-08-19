# -*- coding: utf-8 -*-

# Standard library modules
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4

# Third-party modules
import numpy as np
from pydantic import (BaseModel, ConfigDict, Field, NonNegativeFloat,
                      NonNegativeInt, ValidationError, field_validator,
                      model_validator)

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
    "get_fields",
]


# .................................................................................................
def get_fields(model, required=False) -> list:
    """
    Return a list of all or required fields for the message.
    """
    return [k for k, v in model.model_fields.items() if v.is_required() or not required]


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

    model_config = ConfigDict(validate_assignment=True)

    # NOTE: This field is optional from the user's perspective, but during model validation,
    # it will be automatically generated if not already specified, so in practice this field
    # will never be empty.
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


# .................................................................................................
class DetectorMessageBase(MessageBase):
    """
    Base class for all messages related to a specific detector.
    """

    model_config = ConfigDict(validate_assignment=True)

    detector_name: str = Field(
        ...,
        title="Detector Name",
        description="Name of the detector that sent the message"
    )

    def is_valid_detector(self):
        """
        Ensure the detector name is in the list of supported detectors.
        """
        return self.detector_name in detectors.names


# .................................................................................................
class HeartbeatMessage(DetectorMessageBase):
    """
    Heartbeat detector message.
    """

    model_config = ConfigDict(validate_assignment=True)

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

    model_config = ConfigDict(validate_assignment=True)

    retract_message_uuid: Optional[str] = Field(
        default=None,
        title="Unique message ID",
        description="Unique identifier for the message to retract"
    )

    retract_latest_n: NonNegativeInt = Field(
        default=0,
        title="Retract Latest Flag",
        description="True if the latest message is being retracted",
    )

    retraction_reason: Optional[str] = Field(
        default=None,
        title="Retraction reason",
        description="Reason for retraction",
    )

    @model_validator(mode="before")
    def _set_tier(cls, values):
        values['tier'] = Tier.RETRACTION
        return values

    @model_validator(mode="after")
    def _validate_model(self):
        if self.retract_latest_n > 0 and self.retract_message_uuid is not None:
            raise ValueError("retract_message_uuid cannot be specified when retract_latest_n > 0")

        if self.retract_latest_n == 0 and self.retract_message_uuid is None:
            raise ValueError("Must specify either retract_message_uuid or retract_latest_n > 0")
        return self


# .................................................................................................
class TierMessageBase(DetectorMessageBase):
    """
    Tier base message
    """

    model_config = ConfigDict(validate_assignment=True)

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

    model_config = ConfigDict(validate_assignment=True)

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

    model_config = ConfigDict(validate_assignment=True)

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

    model_config = ConfigDict(validate_assignment=True)

    neutrino_time_utc: str = Field(
        ...,
        title="Neutrino Time (UTC)",
        description="Time of the first neutrino in the event in ISO 8601-1:2019 format"
    )

    @model_validator(mode="before")
    def _set_tier(cls, values):
        values['tier'] = Tier.COINCIDENCE_TIER
        return values

    @field_validator("neutrino_time_utc", mode="before")
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
def compatible_message_types(include_heartbeats=False, **kwargs) -> list:
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

            # Coincidence tier messages can also double as heartbeats
            if include_heartbeats and message_type == CoincidenceTierMessage:
                compatible_message_types.append(HeartbeatMessage)

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
        if message_type == HeartbeatMessage and "detector_status" not in kwargs.keys():
            message = message_type(detector_status="ON", **kwargs)

        else:
            message = message_type(**kwargs)

        messages.append(message)

    if len(messages) == 0:
        raise ValueError("No compatible message types found")

    return messages
