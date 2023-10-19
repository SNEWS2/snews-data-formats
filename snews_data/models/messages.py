# -*- coding: utf-8 -*-

# Standard library modules
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional
from uuid import uuid4

# Third-party modules
from pydantic import (UUID4, BaseModel, Field, NonNegativeFloat,
                      field_validator, model_validator)

# Local modules
from .. import data
from ..__version__ import schema_version


# .................................................................................................
class SNEWSMessageTier(str, Enum):
    HEART_BEAT = "Heartbeat"
    RETRACTION = "Retraction"
    TIME_TIER = "TimeTier"
    SIG_TIER = "SigTier"
    COINCIDENCE_TIER = "CoincidenceTier"


# .................................................................................................
class SNEWSMessageModel(BaseModel):

    id_: str = Field(
        default=None,
        description="Textual identifier for the message"
    )

    uid: UUID4 = Field(
        default_factory=uuid4,
        description="Unique identifier for the message"
    )

    detector_name: str = Field(
        default=None,
        description="Name of the detector that sent the message"
    )

    tier: SNEWSMessageTier = Field(
        ...,
        title="Message Tier",
        description="Message tier",
    )

    sent_time_utc: Optional[str] = Field(
        default=None,
        description="Time the message was sent in ISO format"
    )

    machine_time_utc: str = Field(
        ...,
        description="Time of the event at the detector in ISO format"
    )

    is_pre_sn: bool = Field(
        default=False,
        description="True if the message is a pre-SN alert"
    )

    is_test: bool = Field(
        default=False,
        description="True if the message is a test alert"
    )

    is_firedrill: bool = Field(
        default=False,
        description="True if the message is a fire drill alert"
    )

    meta: Optional[dict] = Field(
        default=None,
        description="Attached metadata"
    )

    schema_version: Optional[str] = Field(
        default=schema_version,
        description="Schema version of the message",
        frozen=True,
    )

    @field_validator("id_")
    def validate_id(cls, v):
        # Check textual ID has at least two sub-strings separated by an underscore
        if len(v.split("_")) < 2:
            raise ValueError("id must have at least two sub-strings separated by an underscore")
        return v

    @field_validator("sent_time_utc", "machine_time_utc")
    def validate_times(cls, v):
        # Check for ISO format
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("Time must be in ISO format")
        return v

    @model_validator(mode="after")
    def validate_model(cls, values):
        # Check that detector exists
        detector = data.detectors.get_by_name(values.detector_name)
        if detector is None:
            raise ValueError(f"Unknown detector name: {values.detector_name}")

        # Set textual ID
        values.id_ = f"{detector.id}_{values.tier.value}_{values.machine_time_utc}"

        # TODO: Check message type
        # Two types: Tier and Command messages. Command messages (listed below) are included in
        # the id field.
        # - hard-reset
        # - test-connection
        # - Get-Feedback
        # - display-heartbeats
        # - Retraction
        # - Heartbeat

        return values


# .................................................................................................
class SNEWSMessageHeartBeatModel(SNEWSMessageModel):
    def __init__(self, **data):
        super().__init__(**data)
        self.tier = SNEWSMessageTier.HEART_BEAT

    detector_status: str = Field(
        ...,
        description="Status of the detector",
        examples=["ON", "OFF"]
    )

    @field_validator("detector_status")
    def validate_detector_status(cls, v):
        if v not in ["ON", "OFF"]:
            raise ValueError("Detector status must be either ON or OFF")
        return v

    @model_validator(mode="after")
    def validate_model(cls, values):
        return


# .................................................................................................
class SNEWSMessageRetractionModel(SNEWSMessageModel):
    def __init__(self, **data):
        super().__init__(**data)
        self.tier = SNEWSMessageTier.COINCIDENCE_TIER

    retract_latest: bool = Field(
        ...,
        description="True if the latest message is being retracted",
    )

    retraction_reason: str = Field(
        ...,
        description="Reason for retraction",
    )

    @model_validator(mode="after")
    def validate_model(cls, values):
        return


# .................................................................................................
class SNEWSMessageTierBaseModel(SNEWSMessageModel):
    neutrino_time_utc: str = Field(
        ...,
        description="Time of the first neutrino in the event in ISO format"
    )

    @field_validator("neutrino_time_utc")
    def validate_neutrino_time(cls, v):
        now = datetime.utcnow()

        # Check for ISO format
        try:
            neutrino_time = datetime.fromisoformat(v)
        except ValueError:
            raise ValueError("neutrino_time_utc must be in ISO format")

        # Check newer than 48 hours ago
        if neutrino_time < now - timedelta(hours=48):
            raise ValueError("neutrino_time_utc must be within 48 hours of now")

        # Check not in the future
        if neutrino_time > now:
            raise ValueError("neutrino_time_utc must be in the past")

        return v

    @model_validator(mode="after")
    def validate_model(cls, values):
        return


# .................................................................................................
class SNEWSMessageTimeTierModel(SNEWSMessageTierBaseModel):
    def __init__(self, **data):
        super().__init__(**data)
        self.tier = SNEWSMessageTier.TIME_TIER

    timing_series: List[str] = Field(
        ...,
        description="Timing series of the event",
    )

    @field_validator("timing_series")
    def validate_timing_series(cls, v):
        # Check for ISO format
        try:
            for t in v:
                datetime.fromisoformat(t)
        except ValueError:
            raise ValueError("Timing series entries must be in ISO format")
        return v

    @model_validator(mode="after")
    def validate_model(cls, values):
        return values


# .................................................................................................
class SNEWSMessageSigTierModel(SNEWSMessageTierBaseModel):
    def __init__(self, **data):
        super().__init__(**data)
        self.tier = SNEWSMessageTier.SIG_TIER

    p_values: List[NonNegativeFloat] = Field(
        ...,
        description="p-values of the event",
    )

    t_bin_width_sec: NonNegativeFloat = Field(
        ...,
        description="Time bin width of the event",
    )

    @field_validator("p_values")
    def validate_p_values(cls, v):
        for p in v:
            if p > 1:
                raise ValueError("p-values must be less than or equal to 1")
        return v

    @field_validator("t_bin_width_sec")
    def validate_t_bin_width(cls, v):
        return v

    @model_validator(mode="after")
    def validate_model(cls, values):
        return values


# .................................................................................................
class SNEWSMessageCoincidenceTierModel(SNEWSMessageTierBaseModel):
    def __init__(self, **data):
        super().__init__(**data)
        self.tier = SNEWSMessageTier.COINCIDENCE_TIER

    p_value: NonNegativeFloat = Field(
        ...,
        description="p-value of coincidence",
        le=1,
    )

    @model_validator(mode="after")
    def validate_model(cls, values):
        return
