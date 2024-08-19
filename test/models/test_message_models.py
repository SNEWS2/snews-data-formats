# -*- coding: utf-8 -*-

# Standard modules
import datetime

# Third-party modules
import hypothesis.strategies as st
import pytest
from hypothesis import given

# Local modules
from snews.data import detectors
from snews.models.messages import (CoincidenceTierMessage, HeartbeatMessage,
                                   RetractionMessage, SignificanceTierMessage,
                                   Tier, TimingTierMessage)

# STRATEGIES ======================================================================================

# Base message
strategy_required_fields_base = {
    "detector_name": st.sampled_from(detectors.names),
    "tier": st.sampled_from(Tier),
    "machine_time_utc": st.datetimes().map(lambda x: x.isoformat()),
    "is_pre_sn": st.booleans(),
    "is_test": st.booleans(),
    "is_firedrill": st.booleans(),
    "meta": st.dictionaries(keys=st.text(), values=st.text()),
}

# Tier base message
strategy_required_fields_tier = {
    **strategy_required_fields_base,
    "p_val": st.floats(min_value=0.0, max_value=1.0),
}

# TimingTier message
strategy_required_fields_tier_timing = {
    **strategy_required_fields_tier,
    "timing_series": st.lists(elements=st.datetimes().map(lambda x: x.isoformat())),
}

# SignalTier message
strategy_required_fields_tier_significance = {
    **strategy_required_fields_tier,
    "p_values": st.lists(elements=st.floats(min_value=0.0, max_value=1.0)),
    "t_bin_width_sec": st.floats(min_value=0.0),
}
# CoincidenceTier message
strategy_required_fields_tier_coincidence = {
    **strategy_required_fields_tier,
    "neutrino_time_utc": st.datetimes(
        max_value=datetime.datetime.now(datetime.UTC).replace(tzinfo=None),
        min_value=datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        - datetime.timedelta(hours=47),
    ).map(lambda x: x.isoformat()),
}

# Heartbeat message
strategy_required_fields_heartbeat = {
    **strategy_required_fields_base,
    "detector_status": st.sampled_from(["OFF", "ON"]),
}

# Retraction message
strategy_required_fields_retraction = {
    **strategy_required_fields_base,
    "retraction_reason": st.text(min_size=1),
}


# TESTS ===========================================================================================


# Timing Tier Test
@given(**strategy_required_fields_tier_timing)
def test_snews_message_model_timing_tier_required(**kwargs):
    TimingTierMessage(**kwargs)


@given(**strategy_required_fields_tier_timing)
def test_snews_message_model_timing_tier_invalid_timing_series(**kwargs):
    with pytest.raises(ValueError) as exc_info:
        msg = TimingTierMessage(**kwargs)
        msg.timing_series = ["1987-02-24T05:31:00Z", "Feb 24, 1987 5:31 AM UTC"]

    assert "Timing series entries must be in ISO 8601-1:2019 format" in str(
        exc_info.value
    )


# Significance Tier Test
@given(**strategy_required_fields_tier_significance)
def test_snews_message_model_sig_tier_required(**kwargs):
    SignificanceTierMessage(**kwargs)


@given(**strategy_required_fields_tier_significance)
def test_snews_message_model_sig_tier_p_values_validation(**kwargs):
    with pytest.raises(ValueError) as exc_info:
        msg = SignificanceTierMessage(**kwargs)
        msg.p_values = [0.5, 1.2, 0.3]

    assert "p-value in list out of range." in str(exc_info.value)


# Coincidence Tier Test
@given(**strategy_required_fields_tier_coincidence)
def test_snews_message_model_coincidence_tier_required(**kwargs):
    CoincidenceTierMessage(**kwargs)


@given(**strategy_required_fields_tier_coincidence)
def test_snews_message_model_coincidence_tier_nu_time_out_of_window(**kwargs):
    with pytest.raises(ValueError) as exc_info:
        msg = CoincidenceTierMessage(**kwargs)
        msg.is_test = False
        msg.neutrino_time_utc = "1987-02-24T05:31:00Z"

    assert "neutrino_time_utc must be within past 48 hours" in str(exc_info.value)


@given(**strategy_required_fields_tier_coincidence)
def test_snews_message_model_coincidence_tier_nu_time_in_future(**kwargs):
    with pytest.raises(ValueError) as exc_info:
        msg = CoincidenceTierMessage(**kwargs)
        msg.is_test = False
        msg.neutrino_time_utc = "2087-02-24T05:31:00Z"

    assert "neutrino_time_utc must be in the past" in str(exc_info.value)


# Heartbeat Tests
@given(**strategy_required_fields_heartbeat)
def test_snews_message_model_heartbeat_required(**kwargs):
    HeartbeatMessage(**kwargs)


@given(**strategy_required_fields_heartbeat)
def test_snews_message_model_heartbeat_invalid_detector(**kwargs):
    msg = HeartbeatMessage(**kwargs)
    msg.detector_name = "Super-Duper-K"

    assert msg.is_valid_detector() is False


@given(**strategy_required_fields_heartbeat)
def test_snews_message_model_heartbeat_invalid_detector_status(**kwargs):
    with pytest.raises(ValueError) as exc_info:
        msg = HeartbeatMessage(**kwargs)
        msg.detector_status = "OK"

    assert "Detector status must be either ON or OFF" in str(exc_info.value)


# Retraction Tests
@given(**strategy_required_fields_retraction)
def test_snews_message_model_retraction_required(**kwargs):
    RetractionMessage(
        retract_latest_n=3,
        **kwargs,
    )

    RetractionMessage(
        retract_message_uuid="1234567890",
        **kwargs
    )


@given(**strategy_required_fields_retraction)
def test_snews_message_model_retraction_validation_both_indicators(**kwargs):
    with pytest.raises(ValueError) as exc_info:
        RetractionMessage(
            retract_latest_n=3,
            retract_message_uuid="1234567890",
            **kwargs,
        )

    assert "retract_message_uuid cannot be specified when retract_latest_n > 0" in str(
        exc_info.value
    )


@given(**strategy_required_fields_retraction)
def test_snews_message_model_retraction_validation_neither_indicator(**kwargs):
    with pytest.raises(ValueError) as exc_info:
        RetractionMessage(
            retract_latest_n=0,
            retract_message_uuid=None,
            **kwargs,
        )

    assert "Must specify either retract_message_uuid or retract_latest_n > 0" in str(
        exc_info.value
    )
