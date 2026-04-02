import requests
import json
import time
import logging

from pathlib import Path

#Forma de ver los errores o warnings de una manera diferente en vez de usar Pirnt
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

#Variables constantes
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
REQUEST_TIMEOUT = 30
RETRY_WAIT = 5
MAX_RETRIES = 3

#Función que crea la sentencia SPARQL para enviar al servidor
def build_query(limit: int, offset: int) -> str:
    """
    Construye la query SPARQL para obtener personas del área tech.
    Usa OPTIONAL para campos que pueden estar vacíos en Wikidata.
    
    - P31  = instancia de        | Q5       = humano
    - P106 = ocupación           | Q82594   = computer scientist
    - P108 = empleador           | Q205375  = software engineer
    - P69  = educado en          | Q15976092= AI researcher
    - P27  = país de ciudadanía  | Q13418253= data scientist
    """
    return f"""
    SELECT ?person ?personLabel ?occupation ?occupationLabel
           ?employer ?employerLabel ?university ?universityLabel
           ?country ?countryLabel
    WHERE {{
        ?person wdt:P31 wd:Q5 ;
                wdt:P106 ?occupation .

        VALUES ?occupation {{
            wd:Q82594
            wd:Q205375
            wd:Q15976092
            wd:Q13418253
            wd:Q1251441
        }}

        OPTIONAL {{ ?person wdt:P108 ?employer . }}
        OPTIONAL {{ ?person wdt:P69  ?university . }}
        OPTIONAL {{ ?person wdt:P27  ?country . }}

        SERVICE wikibase:label {{
            bd:serviceParam wikibase:language "en" .
        }}
    }}
    LIMIT {limit}
    OFFSET {offset}
    """

#Función que trae el json de los datos de la url de Wikidata
def fetch_data(sparql: str) -> dict | None:

    headers = {
        "User-Agent": "CareerPathAnalyzer/1.0 (proyecto educativo)",
        "Accept":     "application/sparql-results+json"
    }

    params = { "query": sparql, "format": "json"}

    for intento in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(WIKIDATA_ENDPOINT, headers = headers, params = params, timeout = REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout en intento {intento}/{MAX_RETRIES}: {e}")

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error while fetching data: {e}")
        
        if intento < MAX_RETRIES: time.sleep(RETRY_WAIT)

    logger.error("Number of attempts failed")
    return None

#Función para parsear la data de el json
def parse_response(raw: dict) -> list[dict]:
    try:
        bindings = raw["results"]["bindings"]
    except Exception as e:
        logger.error(f"Error while tracking bindings from Wikidata: {e}")
        return []
    
    result = list()
    for item in bindings:
        result.append({key: item[key]["value"] for key in item })

    logger.info(f"Parsed {len(result)} records from response.")
    return result


    