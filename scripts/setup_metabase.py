import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from indicators import INDICATORS, TABS


BASE_URL = os.environ.get("METABASE_URL", "http://localhost:3000").rstrip("/")
EMAIL = os.environ.get("METABASE_EMAIL", "calificar@uvg.edu.gt")
PASSWORD = os.environ.get("METABASE_PASSWORD", "secret123+")


def request(method, path, payload=None, token=None, expected=(200, 201, 202, 204)):
    data = None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Metabase-Session"] = token
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8")
            if resp.status not in expected:
                raise RuntimeError(f"{method} {path} devolvió {resp.status}: {body}")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} falló con {exc.code}: {body}") from exc


def wait_for_metabase():
    print("Esperando a que Metabase esté listo...")
    for _ in range(90):
        try:
            props = request("GET", "/api/session/properties")
            if "setup-token" in props:
                return props
        except Exception as exc:
            print(f"Metabase aún no responde: {exc}")
        time.sleep(5)
    raise TimeoutError("Metabase no quedó listo dentro del tiempo esperado.")


def setup_or_login(props):
    setup_token = props.get("setup-token")
    if setup_token and not props.get("has-user-setup"):
        payload = {
            "token": setup_token,
            "user": {
                "first_name": "Usuario",
                "last_name": "Calificador",
                "email": EMAIL,
                "password": PASSWORD,
            },
            "prefs": {
                "site_name": "RetailMax Ventas",
                "site_locale": "es",
                "allow_tracking": False,
            },
            "database": {
                "engine": "postgres",
                "name": "RetailMax PostgreSQL",
                "details": {
                    "host": os.environ.get("POSTGRES_HOST", "postgres"),
                    "port": int(os.environ.get("POSTGRES_PORT", "5432")),
                    "dbname": os.environ.get("POSTGRES_DB", "retailmax"),
                    "user": os.environ.get("POSTGRES_USER", "retailmax"),
                    "password": os.environ.get("POSTGRES_PASSWORD", "retailmax123"),
                    "ssl": False,
                    "tunnel-enabled": False,
                },
            },
        }
        print("Configurando instalación inicial de Metabase...")
        result = request("POST", "/api/setup", payload)
        token = result.get("id")
        if token:
            return token

    print("Iniciando sesión en Metabase...")
    result = request("POST", "/api/session", {"username": EMAIL, "password": PASSWORD})
    return result["id"]


def find_database_id(token):
    databases = request("GET", "/api/database", token=token).get("data", [])
    for database in databases:
        if database.get("name") == "RetailMax PostgreSQL":
            return database["id"]

    payload = {
        "engine": "postgres",
        "name": "RetailMax PostgreSQL",
        "details": {
            "host": os.environ.get("POSTGRES_HOST", "postgres"),
            "port": int(os.environ.get("POSTGRES_PORT", "5432")),
            "dbname": os.environ.get("POSTGRES_DB", "retailmax"),
            "user": os.environ.get("POSTGRES_USER", "retailmax"),
            "password": os.environ.get("POSTGRES_PASSWORD", "retailmax123"),
            "ssl": False,
            "tunnel-enabled": False,
        },
    }
    print("Creando conexión a PostgreSQL en Metabase...")
    return request("POST", "/api/database", payload, token=token)["id"]


def validate_sql(database_id, token):
    print("Validando consultas SQL contra PostgreSQL...")
    for indicator in INDICATORS:
        payload = {
            "database": database_id,
            "type": "native",
            "native": {"query": indicator["sql"]},
            "parameters": [],
        }
        request("POST", "/api/dataset", payload, token=token)


def existing_by_name(model, name, token):
    result = request(
        "GET",
        f"/api/search?q={urllib.parse.quote(name)}&models={model}",
        token=token,
    ).get("data", [])
    for item in result:
        if item.get("name") == name:
            return item
    return None


def create_cards(database_id, token):
    cards = {}
    for indicator in INDICATORS:
        existing = existing_by_name("card", indicator["name"], token)
        if existing:
            cards[indicator["key"]] = existing["id"]
            continue

        payload = {
            "name": indicator["name"],
            "description": indicator["description"],
            "display": indicator["display"],
            "dataset_query": {
                "database": database_id,
                "type": "native",
                "native": {"query": indicator["sql"]},
            },
            "visualization_settings": {},
        }
        created = request("POST", "/api/card", payload, token=token)
        cards[indicator["key"]] = created["id"]
        print(f"Card creado: {indicator['name']}")
    return cards


def create_dashboard(token):
    name = "Dashboard de Ventas - RetailMax"
    existing = existing_by_name("dashboard", name, token)
    if existing:
        return existing["id"]
    payload = {
        "name": name,
        "description": "Dashboard del Área 1: Ventas, construido únicamente con Native SQL.",
    }
    created = request("POST", "/api/dashboard", payload, token=token)
    return created["id"]


def dashboard_cards_payload(cards):
    tab_ids = {TABS[0]: -1, TABS[1]: -2}
    positions = {
        TABS[0]: [(0, 0, 6, 3), (6, 0, 6, 3), (12, 0, 6, 3), (0, 3, 18, 6), (0, 9, 9, 6), (9, 9, 9, 6)],
        TABS[1]: [(0, 0, 9, 6), (9, 0, 9, 6), (0, 6, 9, 6), (9, 6, 9, 6), (0, 12, 9, 6), (9, 12, 9, 6)],
    }
    used = {tab: 0 for tab in TABS}
    dashcards = []
    next_dashcard_id = -10
    for indicator in INDICATORS:
        tab = indicator["tab"]
        col, row, size_x, size_y = positions[tab][used[tab]]
        used[tab] += 1
        dashcards.append(
            {
                "id": next_dashcard_id,
                "card_id": cards[indicator["key"]],
                "row": row,
                "col": col,
                "size_x": size_x,
                "size_y": size_y,
                "dashboard_tab_id": tab_ids[tab],
                "parameter_mappings": [],
                "series": [],
                "visualization_settings": {},
            }
        )
        next_dashcard_id -= 1
    return {
        "dashcards": dashcards,
        "tabs": [{"id": tab_ids[name], "name": name} for name in TABS],
        "parameters": [],
        "width": "fixed",
    }


def update_dashboard(dashboard_id, cards, token):
    print("Publicando dashboard con tabs e indicadores...")
    payload = dashboard_cards_payload(cards)
    payload.update(
        {
            "name": "Dashboard de Ventas - RetailMax",
            "description": "Dashboard del Área 1: Ventas, construido únicamente con Native SQL.",
        }
    )
    request("PUT", f"/api/dashboard/{dashboard_id}", payload, token=token)


def main():
    props = wait_for_metabase()
    token = setup_or_login(props)
    database_id = find_database_id(token)
    try:
        request("POST", f"/api/database/{database_id}/sync_schema", token=token, expected=(200, 202, 204))
    except Exception as exc:
        print(f"No se pudo forzar sync_schema, se continúa porque Metabase puede sincronizar en segundo plano: {exc}")
    time.sleep(5)
    validate_sql(database_id, token)
    cards = create_cards(database_id, token)
    dashboard_id = create_dashboard(token)
    update_dashboard(dashboard_id, cards, token)
    print("Metabase quedó configurado correctamente.")
    print(f"Dashboard: {BASE_URL}/dashboard/{dashboard_id}")


if __name__ == "__main__":
    main()
