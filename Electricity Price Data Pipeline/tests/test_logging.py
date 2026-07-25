import logging
import tempfile
import unittest
from pathlib import Path

import logging_config


class TestLoggingConfiguration(unittest.TestCase):
    def test_configure_logging_creates_file_handler_and_logger(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "pipeline.log"
            logger = logging_config.configure_logging(log_file=log_path, level=logging.INFO)

            self.assertEqual(logger.name, "electricity_pipeline")
            self.assertEqual(logger.level, logging.INFO)
            self.assertTrue(any(isinstance(handler, logging.FileHandler) for handler in logger.handlers))
            self.assertTrue(log_path.exists())

            logger.info("test message")

            self.assertTrue(log_path.exists())


if __name__ == "__main__":
    unittest.main()
