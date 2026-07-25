import logging
import tempfile
from pathlib import Path

import logging_config


def test_configure_logging_creates_file_handler_and_logger():
    with tempfile.TemporaryDirectory() as temp_dir:
        log_path = Path(temp_dir) / "pipeline.log"
        logger = logging_config.configure_logging(log_file=log_path, level=logging.INFO)

        assert logger.name == "electricity_pipeline"
        assert logger.level == logging.INFO
        assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)
        assert log_path.exists() is False

        logger.info("test message")

        assert log_path.exists() is True
