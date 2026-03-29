import requests
import json

from pathlib import Path

WIKI_URL = ""

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

if __name__ == "__main__":
    query = build_query(limit=100, offset=0)
    print(query)