import json
from datetime import date


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Devuelve la fecha actual. Úsala cuando el usuario pregunte por la fecha, el día de hoy o cálculos de tiempo.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Busca información actualizada en internet. Úsala SOLO cuando la respuesta no esté en los documentos internos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "El texto a buscar en internet"
                    }
                },
                "required": ["query"]
            }
        }
    }
]


def get_current_date() -> str:
    return f"Hoy es {date.today().strftime('%d/%m/%Y')}."


def search_web(query: str) -> str:
    from openai import OpenAI
    client = OpenAI()
    response = client.responses.create(
        model="gpt-4o-mini",
        tools=[{"type": "web_search_preview"}],
        input=query
    )
    for item in response.output:
        if item.type == "message":
            return item.content[0].text
    return "No se encontraron resultados."


def execute_tool(name: str, arguments: str) -> str:
    args = json.loads(arguments) if arguments else {}
    if name == "get_current_date":
        return get_current_date()
    elif name == "search_web":
        return search_web(args["query"])
    return "Herramienta no encontrada."
