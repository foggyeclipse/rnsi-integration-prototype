import logging
from typing import dict

from fastapi import FastAPI, HTTPException

from app.config import settings
from app.database import save_records
from app.nsi_client import download_dictionary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Загрузчик справочников НСИ Минздрава России",
    description=(
        "Сервис предназначен для загрузки нормативно-справочной информации "
        "из реестра НСИ Минздрава РФ и её сохранения в базе данных PostgreSQL."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Справочники НСИ",
            "description": "Операции загрузки и сохранения справочников",
        }
    ],
)


@app.get("/dictionary", tags=["Справочники НСИ"])
def get_dictionary(identifier: str) -> dict:
    """Получить справочник по идентификатору без сохранения."""
    try:
        data = download_dictionary(identifier)
        return {"identifier": identifier, "records": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@app.post("/dictionary/save", tags=["Справочники НСИ"])
def save_single_dictionary(identifier: str) -> dict:
    """Загрузить и сохранить справочник по идентификатору."""
    try:
        data = download_dictionary(identifier)
        count = save_records(identifier, data)
        return {"status": "saved", "identifier": identifier, "records": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from None


@app.post("/dictionary/save_all", tags=["Справочники НСИ"])
def save_all_dictionaries() -> dict:
    """Загрузить и сохранить все справочники из конфигурации."""
    summary = []

    for identifier in settings.DICTIONARIES:
        try:
            data = download_dictionary(identifier)
            count = save_records(identifier, data)
            summary.append({"identifier": identifier, "records": count, "status": "ok"})
        except Exception as e:
            logger.error("Failed to process %s: %s", identifier, e)
            summary.append(
                {"identifier": identifier, "records": 0, "status": f"error: {e!s}"}
            )

    return {"summary": summary}


@app.get("/dictionary/download_all", tags=["Справочники НСИ"])
def download_all_dictionaries() -> dict:
    """Получить все справочники из конфигурации без сохранения."""
    result = {}

    for identifier in settings.DICTIONARIES:
        try:
            data = download_dictionary(identifier)
            result[identifier] = {"records": len(data)}
        except Exception as e:
            result[identifier] = {"error": str(e)}

    return result


@app.post("/dictionary/sync_all", tags=["Справочники НСИ"])
def sync_all_dictionaries() -> dict:
    """Выполнить полную синхронизацию справочников (для планировщика)."""
    logger.info("Запуск плановой синхронизации справочников НСИ")
    return save_all_dictionaries()
