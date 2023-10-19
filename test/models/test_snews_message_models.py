# -*- coding: utf-8 -*-

# Standard modules
from datetime import datetime, timedelta

# Third-party modules
import hypothesis.strategies as st
from hypothesis import given

# Local modules
from snews_data import data, models

# sent_time_utc: Optional[str]
# meta: Optional[dict]
# schema_version: Optional[str]

# Base message
strategy_required_fields_base = {
    "detector_name": st.sampled_from(data.detectors.names),
    "tier": st.sampled_from(models.messages.SNEWSMessageTier),
    "machine_time_utc": st.datetimes().map(lambda x: x.isoformat()),
    "is_pre_sn": st.booleans(),
    "is_test": st.booleans(),
    "is_firedrill": st.booleans(),
    "meta": st.dictionaries(keys=st.text(), values=st.text()),
}


@given(**strategy_required_fields_base)
def test_snews_message_model_base_required(**kwargs):
    models.messages.SNEWSMessageModel(**kwargs)


# TimingTier message
strategy_required_fields_tier = {
    **strategy_required_fields_base,
    "neutrino_time_utc": st.datetimes(
        max_value=datetime.utcnow(),
        min_value=datetime.utcnow()-timedelta(hours=47)
    ).map(lambda x: x.isoformat()),
}

strategy_required_fields_tier_time = {
    **strategy_required_fields_tier,
    "timing_series": st.lists(elements=st.datetimes().map(lambda x: x.isoformat())),
}


@given(**strategy_required_fields_tier_time)
def test_snews_message_model_time_tier_required(**kwargs):
    models.messages.SNEWSMessageTimeTierModel(**kwargs)


# SignalTier message
strategy_required_fields_tier_sig = {
    **strategy_required_fields_tier,
    "p_values": st.lists(elements=st.floats(min_value=0.0, max_value=1.0)),
    "t_bin_width_sec": st.floats(min_value=0.0),
}


@given(**strategy_required_fields_tier_sig)
def test_snews_message_model_sig_tier_required(**kwargs):
    models.messages.SNEWSMessageSigTierModel(**kwargs)


# CoincidenceTier message
strategy_required_fields_tier_coincidence = {
    **strategy_required_fields_tier,
    "p_value": st.floats(min_value=0.0, max_value=1.0),
}


@given(**strategy_required_fields_tier_coincidence)
def test_snews_message_model_coincidence_tier_required(**kwargs):
    models.messages.SNEWSMessageCoincidenceTierModel(**kwargs)


# Heartbeat message
strategy_required_fields_heartbeat = {
    **strategy_required_fields_base,
    "detector_status": st.sampled_from(["OFF", "ON"]),
}


@given(**strategy_required_fields_heartbeat)
def test_snews_message_model_heartbeat_required(**kwargs):
    models.messages.SNEWSMessageHeartBeatModel(**kwargs)


def test_snews_message_model_heartbeat_detector_status():
    # TODO
    return


# Retraction message
strategy_required_fields_retraction = {
    **strategy_required_fields_base,
    "retract_latest": st.booleans(),
    "retraction_reason": st.text(),
}


@given(**strategy_required_fields_retraction)
def test_snews_message_model_retraction_required(**kwargs):
    models.messages.SNEWSMessageRetractionModel(**kwargs)
