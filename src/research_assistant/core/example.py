from research_assistant.utils.logging import get_logger, setup_logging

# Set up logging configuration
setup_logging()

# Get a logger for this module
logger = get_logger(__name__)

def example_function():
    """Example function demonstrating different logging levels."""
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    try:
        # Simulate an error
        raise ValueError("Example error")
    except Exception as e:
        logger.exception("An error occurred: %s", str(e))

if __name__ == "__main__":
    example_function() 