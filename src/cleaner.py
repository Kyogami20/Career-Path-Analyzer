import logging
import re

logging.basicConfig(
    level= logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

def extract_ID(url: str) -> str:
    if not url:
        logger.warning("Not url given")
        return ""
    
    return url.split("/")[-1]