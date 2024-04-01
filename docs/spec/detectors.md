---
title: SNEWS Data Specification — Detectors
summary: Specification for SNEWS member detectors.
---

# SNEWS Data Specification — Detectors

## Introduction

This document describes the specification for SNEWS member detectors. It is
intended to be used as a reference for the SNEWS data format.

## Detector Type Data Model

The following detector types are defined as an enum:
```
WATER_CERENKOV
LIQUID_SCINTILLATOR
LIQUID_ARGON
BUBBLE_CHAMBER
HIGH_Z
OTHER
```

## Detector Data Model

| Name | Type | Description | Constraints |
| ---- | ---- | ----------- | ----------- |
| `id` | Int | Unique ID of the detector | |
| `name` | String | Common name of the detector | |
| `name_full` | String | Full name of the detector | |
| `type` | Detector Type (enum) | Type of detector | |
| `experiment` | String | Name of neutrino experiment | |
| `mass_kt` | Float | Mass of detector in kilotons | Min: 0 |
| `depth_meters` | Float | Dept of detector in meters | Min: 0 |
| `depth_mwe` | Float | Depth of detector in meters water equivalent | Min: 0 |
| `facility` | String | Name of facility where detector is located | |
| `latitude` | Float | Latitude of detector in degrees | Min: -90 <br> Max: 90 |
| `longitude` | Float | Longitude of detector in degrees | Min: -180 <br> Max: 180 |
| `city` | String | City where detector is located | |
| `region` | String | State/province/region where detector is located | |
| `country` | String | Country where detector is located | |
| `website` | String | Website for detector | |
| `logo` | String | URL to logo for detector | |
| `snews_member_status` | boolean | Whether detector is a SNEWS member | |
| `snews_member_since` | DateTime | Date detector became a SNEWS member | |
