# -*- coding: utf-8 -*-

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
def test_create_messages_function():
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
