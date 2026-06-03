import os
import subprocess
import sys

from indicators import INDICATORS


def run_sql(sql):
    env = os.environ.copy()
    env["PGPASSWORD"] = env.get("POSTGRES_PASSWORD", "retailmax123")
    cmd = [
        "docker",
        "compose",
        "exec",
        "-T",
        "postgres",
        "psql",
        "-U",
        env.get("POSTGRES_USER", "retailmax"),
        "-d",
        env.get("POSTGRES_DB", "retailmax"),
        "-v",
        "ON_ERROR_STOP=1",
        "-c",
        sql,
    ]
    return subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(__file__)), text=True, capture_output=True)


def main():
    failures = 0
    checks = {
        "tablas": "SELECT COUNT(*) AS tablas FROM information_schema.tables WHERE table_schema = 'public';",
        "pedidos": "SELECT COUNT(*) AS pedidos FROM pedido;",
        "detalles": "SELECT COUNT(*) AS detalles FROM detalle_pedido;",
        "pagos": "SELECT COUNT(*) AS pagos FROM pago;",
    }
    for name, sql in checks.items():
        result = run_sql(sql)
        if result.returncode != 0:
            failures += 1
            print(f"[ERROR] Validación {name}: {result.stderr}")
        else:
            print(f"[OK] Validación {name}")

    for indicator in INDICATORS:
        result = run_sql(indicator["sql"])
        if result.returncode != 0:
            failures += 1
            print(f"[ERROR] {indicator['name']}: {result.stderr}")
        else:
            print(f"[OK] {indicator['name']}")

    if failures:
        sys.exit(1)
    print("Todas las validaciones SQL finalizaron correctamente.")


if __name__ == "__main__":
    main()
