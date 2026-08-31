"""
Reads a curriculum package from the repository and validates it before any
database write is attempted.

The curriculum lives outside the Django project, at the repository root, and is
validated by ``scripts/validate_curriculum.py`` — the same validator GitHub
Actions runs. It is loaded by path rather than by import so the backend does not
require the repository root on ``PYTHONPATH``.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path

from django.conf import settings

# back-end/ -> repository root
REPO_ROOT = Path(settings.BASE_DIR).parent
TRACKS_ROOT = REPO_ROOT / 'tracks'
SCHEMAS_ROOT = REPO_ROOT / 'schemas'
VALIDATOR_PATH = REPO_ROOT / 'scripts' / 'validate_curriculum.py'


class CurriculumError(Exception):
    """Raised when a curriculum package is missing, unreadable, or invalid."""


def load_validator():
    """Import the repository-root validator module by file path."""
    if not VALIDATOR_PATH.exists():
        raise CurriculumError(f'Curriculum validator not found at {VALIDATOR_PATH}.')

    spec = importlib.util.spec_from_file_location('progressio_curriculum_validator', VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise CurriculumError(f'Curriculum validator at {VALIDATOR_PATH} could not be loaded.')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def available_tracks():
    """Return the sorted IDs of every track directory that holds a curriculum package."""
    if not TRACKS_ROOT.exists():
        return []
    return sorted(
        path.name
        for path in TRACKS_ROOT.iterdir()
        if (path / 'curriculum' / 'curriculum.yaml').exists()
    )


def track_dir(track_id):
    """Resolve a track ID to its curriculum directory."""
    path = TRACKS_ROOT / track_id / 'curriculum'
    if not (path / 'curriculum.yaml').exists():
        known = ', '.join(available_tracks()) or 'none'
        raise CurriculumError(f"No curriculum package for track '{track_id}'. Available: {known}.")
    return path


def _read(path):
    """Load one JSON-compatible YAML document."""
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as error:
        raise CurriculumError(f'{path.name}: {error}') from error


def _read_dir(folder):
    if not folder.exists():
        return []
    return [_read(path) for path in sorted(folder.glob('*.yaml'))]


def load_package(track_id):
    """
    Validate and load one curriculum package.

    Validation runs first and raises before anything is returned, so an invalid
    package can never reach the importer.
    """
    directory = track_dir(track_id)
    validator = load_validator()

    try:
        # The validator prints a summary for CI; callers here want it quiet.
        with contextlib.redirect_stdout(io.StringIO()):
            validator.validate(directory, SCHEMAS_ROOT)
    except ValueError as error:
        raise CurriculumError(f'Curriculum package is invalid: {error}') from error

    return {
        'track_id': track_id,
        'directory': directory,
        'manifest': _read(directory / 'curriculum.yaml'),
        'version': _read(directory / 'version.yaml'),
        'competencies': _read_dir(directory / 'competencies'),
        'skills': _read_dir(directory / 'skills'),
        'resources': _read_dir(directory / 'resources'),
        'assessments': _read_dir(directory / 'assessments'),
    }
