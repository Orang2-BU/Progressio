"""
Progressio curriculum: the measurement standard the platform grades against.

Layout:
    schemas/    entity contracts, one JSON Schema per entity type
    tracks/     one directory per career track, holding its curriculum package
    tests/      validation suite plus valid and invalid fixtures
    validator.py  dependency-free validator, run by CI and by the backend importer
"""
