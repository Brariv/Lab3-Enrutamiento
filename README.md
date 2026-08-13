# Lab 3 — Protocolos de Enrutamiento (jumpstart)

Esqueleto funcional de Link State (HELLO, LSA, flooding con seq/ttl, Dijkstra) + capa de
datos con Hamming(7,4), siguiendo el protocolo acordado con las otras 2 parejas
(`Lab 3 Protocolo Proposal.pdf`). Corre local por ahora (`127.0.0.1` + puertos distintos).

El Hamming se reutiliza de `src/algoritmos/correccionErrores.py` (implementación genérica
ya hecha para el Lab 2), aplicada en bloques de 4 bits desde `src/hamming/` para cumplir
específicamente Hamming(7,4). `Extras/` es la demo de capas del Lab 2 (login/withdraw/logout
con su propio framing) y se deja como referencia, sin relación directa con `src/node.py`.

## Requisitos

- Python 3.10+
- `pip install -r requirements.txt` (solo para correr los tests)

## Configuración

- `config/nodos.json`: IP y puerto (plano de datos) de cada nodo. El puerto de control
  se calcula automáticamente como `puerto + 1000`.
- `config/topologia.json`: vecinos directos y costo de enlace de cada nodo (placeholder,
  reemplacen por la topología real que les asignaron).

**Importante**: los ids (`A`, `B`, ...) son solo para pruebas locales. En el protocolo
acordado, `origin`/`destination`/`from` deben ser la IP real (Tailscale) del nodo — antes
de la prueba de interoperabilidad con las otras parejas, cambien los ids de
`config/nodos.json` por esas IPs.

## Correr nodos router localmente

```bash
python -m src.node A
python -m src.node B
# ...un proceso por nodo, cada uno en su propia terminal
```

Cada nodo imprime su tabla (`data/nodo_<id>_tabla_enrutamiento.csv`) al recalcularla.

## Cliente/servidor de prueba (ATM–Banco)

```bash
python -m src.endpoints.server BANK <gateway_id>
python -m src.endpoints.client ATM <gateway_id> BANK
```

(`src/endpoints/atm_client.py` y `bank_server.py` quedaron como alias por compatibilidad;
usen `client.py`/`server.py`.)

## Tests

```bash
pytest
```

## Qué queda pendiente (ver TODO.md del repo)

- Recalcular rutas / avisar caída de enlace cuando HELLO detecta un vecino caído
  (ahora mismo `on_link_change` solo maneja el caso "UP").
- Persistencia del grafo entre reinicios.
- Lógica real de autenticación/saldo en `src/data/banking.py` (ahora responde "ok" siempre)
  — podría integrarse con el diccionario `ACCOUNTS` de `Extras/server.py`.
- Logging a archivo (`logs/nodo_<id>.log`) en vez de solo stdout.
- Reintentos/backoff en sockets caídos.
- Confirmar con las otras 2 parejas si el `payload` u otros campos del protocolo cambian.
