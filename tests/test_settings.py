import os

from config import settings


def test_input_file_exists():
    # Ensure input_file points to a valid path
    assert os.path.exists(settings.CONFIG["input_file"])


def test_output_file_name():
    # Ensure output file is prefixed correctly
    output_file = settings.CONFIG["output_file"]
    assert os.path.basename(output_file).startswith("Enriched_")
