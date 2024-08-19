# -*- coding: utf-8 -*-

# Third-party modules
import pytest

# Local modules
from snews import models


# .................................................................................................
def test_import_all_models():
    models.__all__
    assert True


# .................................................................................................
def test_import_detector_models():
    expected = models.detectors.__all__
    actual = models.detectors.__dir__()
    assert expected == actual


# .................................................................................................
def test_create_messages_function_success():
    inputs = {
        "detector_name": "Super-K",
        "neutrino_time_utc": "2012-06-09T15:31:08.109876",
        "machine_time_utc": "2012-06-09T15:30:00.009876",
        "is_firedrill": False,
        "is_test": True,
    }

    msgs = models.messages.create_messages(**inputs)
    message_types = [type(msg) for msg in msgs]
    assert message_types == [models.messages.CoincidenceTierMessage]


# .................................................................................................
def test_create_messages_function_no_compatible_messages():
    with pytest.raises(ValueError) as exc_info:
        models.messages.create_messages()

    assert "No compatible message types found" in str(exc_info.value)


# .................................................................................................
def test_create_messages_function_with_heartbeats():
    inputs = {
        "detector_name": "Super-K",
        "neutrino_time_utc": "2012-06-09T15:31:08.109876",
        "machine_time_utc": "2012-06-09T15:30:00.009876",
        "is_firedrill": False,
        "is_test": True,
    }

    msgs = models.messages.create_messages(**inputs, include_heartbeats=True)
    message_types = [type(msg) for msg in msgs]
    assert message_types == [
        models.messages.CoincidenceTierMessage,
        models.messages.HeartbeatMessage
    ]


# .................................................................................................
def test_get_message_fields():
    inputs = {
        "detector_name": "Super-K",
        "detector_status": "ON",
    }

    msg = models.messages.HeartbeatMessage(**inputs)
    fields = set(models.messages.get_fields(msg))
    req_fields = set(models.messages.get_fields(msg, required=True))

    expected_req_fields = set([
        "detector_name",
        "detector_status",
        "tier"
    ])

    expected_fields = set([
        *expected_req_fields,
        "id",
        "uuid",
        "sent_time_utc",
        "machine_time_utc",
        "is_pre_sn",
        "is_test",
        "is_firedrill",
        "meta",
        "schema_version"
    ])

    assert fields == expected_fields and req_fields == expected_req_fields
