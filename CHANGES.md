# Change log for SNEWS Data Formats

## v1.2.0 (unreleased)

* Added 5 new fields to `TimingTierMessage` (PR https://github.com/SNEWS2/snews-data-formats/pull/20).
* Force time series to be ints, not ISO time stamps (PR https://github.com/SNEWS2/snews-data-formats/pull/15).

## v1.1.0 (8 May 2025)

* Changed timing schema so it doesn't drop `neutrino_time_utc` field (PR https://github.com/SNEWS2/snews-data-formats/pull/12).

## v1.0.0 (19 Aug 2024)

First release of SNEWS Data Formats, refactored from utility classes in SNEWS Publishing Tools.

* Update model json schemas (PR https://github.com/SNEWS2/snews-data-formats/pull/10).
* Clean up test and models (PR https://github.com/SNEWS2/snews-data-formats/pull/9).
* Feature get fields (PR https://github.com/SNEWS2/snews-data-formats/pull/8).
* Fix coincidence tier messages (PR https://github.com/SNEWS2/snews-data-formats/pull/7).
* Remove pydantic and numpy deprecated features (PR https://github.com/SNEWS2/snews-data-formats/pull/6).
* Lightly refactor messages (PR https://github.com/SNEWS2/snews-data-formats/pull/5).
