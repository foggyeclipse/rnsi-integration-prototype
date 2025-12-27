import requests
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def parse_nsi_response(data: list[dict]) -> list[dict]:
    """Convert NSI response format to list of flat dictionaries."""
    return [{item["column"]: item["value"] for item in row} for row in data]


def download_dictionary(identifier: str) -> list[dict]:
    """Download all pages of a dictionary from NSI API and return merged records."""
    all_records = []
    page = 1

    logger.info("Starting download: %s (page size: %d)", identifier, settings.PAGE_SIZE)

    while True:
        params = {
            "identifier": identifier,
            "userKey": settings.USER_KEY,
            "page": page,
            "size": settings.PAGE_SIZE,
        }

        try:
            response = requests.get(
                settings.NSI_BASE_URL,
                params=params,
                verify=False,
                timeout=60,
            )
            response.raise_for_status()
            json_data = response.json()

            if json_data.get("result") != "OK":
                raise ValueError(f"API error: {json_data}")

            page_data = parse_nsi_response(json_data.get("list", []))
            all_records.extend(page_data)

            logger.info("Page %d downloaded: %d records", page, len(page_data))

            if len(page_data) < settings.PAGE_SIZE:
                break

            page += 1

        except requests.RequestException as e:
            logger.error("Request failed for %s (page %d): %s", identifier, page, e)
            raise
        except Exception as e:
            logger.error("Unexpected error for %s (page %d): %s", identifier, page, e)
            raise

    logger.info("Download complete: %s — %d records total", identifier, len(all_records))
    return all_records