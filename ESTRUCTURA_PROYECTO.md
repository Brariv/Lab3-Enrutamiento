# Lab 3 — Estructura de archivos/carpetas (actualizado, ya implementado)

Basado en el checklist (`TODO.md`) y el protocolo acordado con las otras 2 parejas (`Lab 3 Protocolo Proposal.pdf`: HELLO, LSA con `seq`/`ttl`, JSON de datos ATM–Servidor). Refleja el estado real del repo, integrando el código del Lab 2 que ya existía (`Extras/`, `src/algoritmos/`).

```
Lab3-Enrutamiento/
├── README.md                        # instalación, uso, cómo correr cada nodo
├── requirements.txt                 # deps para tests (pytest)
├── config/
│   ├── topologia.json               # vecinos + costos iniciales por nodo (placeholder)
│   └── nodos.json                   # IP:puerto de cada nodo (routers, ATM, servidor)
├── src/
│   ├── node.py                      # entry point: lanza HELLO, LSA, Dijkstra y forwarding en paralelo
│   ├── algoritmos/                  # --- reusado del Lab 2 ---
│   │   ├── correccionErrores.py     # Hamming genérico (m, r) — base real del Hamming(7,4)
│   │   └── deteccionErrores.py      # Fletcher / CRC-32 (no requeridos por el enunciado de Lab 3)
│   ├── control/                     # --- Plano de control (3.1) ---
│   │   ├── hello.py                 # envío/recepción HELLO, timeout → enlace caído
│   │   ├── lsa.py                   # construcción del LSA, flooding, control de seq y ttl
│   │   ├── graph.py                 # construcción del grafo de la red a partir de LSAs
│   │   └── dijkstra.py              # cálculo de rutas más cortas → nodo_tabla_enrutamiento.csv
│   ├── data/                        # --- Plano de datos (3.2) ---
│   │   ├── logic.py                 # capa de red: lee CSV, resuelve siguiente salto, reenvía por socket
│   │   ├── messages.py              # serializa/deserializa {nodo_origen, nodo_destino, mensaje}
│   │   ├── banking.py               # payloads AUTH / WITHDRAW / ERROR / LOGOUT del protocolo
│   │   └── forwarding.py            # alias obsoleto → reexporta desde logic.py
│   ├── hamming/                     # --- envoltorio Hamming(7,4) sobre algoritmos/ ---
│   │   ├── bits.py                  # texto UTF-8 ↔ bits (equivalente a Extras/capas/presentacion.py)
│   │   ├── encode.py                # bloques de 4 bits → hamming_codificar() en cada uno
│   │   └── decode.py                # bloques de 7 bits → hamming_decodificar() en cada uno
│   ├── endpoints/                   # --- Cliente y servidor (no-routers) ---
│   │   ├── client.py                # nodo cliente (ATM) → gateway router
│   │   ├── server.py                # nodo servidor (banco) → gateway router
│   │   ├── atm_client.py            # alias obsoleto → reexporta desde client.py
│   │   └── bank_server.py           # alias obsoleto → reexporta desde server.py
│   └── net/
│       └── sockets_utils.py         # helpers TCP compartidos (send_line, start_line_server)
├── Extras/                          # demo de capas del Lab 2 (login/withdraw/logout), referencia
│   ├── server.py
│   └── capas/ (aplicacion, presentacion, enlace, transmision)
├── data/
│   └── nodo_<id>_tabla_enrutamiento.csv  # generado en runtime, uno por nodo
├── logs/
│   └── <id>.out                     # útil para depurar convergencia del flooding
├── tests/
│   ├── test_hamming.py              # unit tests de encode/decode
│   ├── test_dijkstra.py             # unit tests de cálculo de rutas
│   └── test_lsa_flooding.py         # simula seq/ttl y anti-loop
└── docs/
    └── reporte.pdf                  # reporte final a entregar en Canvas
```

## Mapeo checklist → archivo

### 0. Antes de programar
- Formato de mensajes acordado → ya está en `Lab 3 Protocolo Proposal.pdf`; transcríbelo a `docs/protocolo.md` como referencia rápida del equipo.
- Vecinos/costos iniciales → `config/topologia.json`.
- IP/puerto por nodo → `config/nodos.json`.

### 1. Plano de control
- HELLO → `src/control/hello.py`
- LSA (`type`, `origin`, `seq`, `ttl`, `links`, `from`) → `src/control/lsa.py`
- Anti-loop (seq guardado por `origin`, `ttl` decreciente) → misma clase/módulo `src/control/lsa.py` (tabla `last_seq` en memoria)
- Grafo de la red → `src/control/graph.py`
- Dijkstra → `src/control/dijkstra.py`
- Salida: `data/nodo_tabla_enrutamiento.csv`

### 2. Plano de datos y capas
- Formato `{nodo_origen, nodo_destino, mensaje}` + `origin`/`destination`/`payload` → `src/data/messages.py`
- Capa de red (lee CSV, reenvía) → `src/data/logic.py`
- Hamming 7,4 (encode/decode, pasos 1–9 del PDF) → `src/hamming/encode.py` y `src/hamming/decode.py`, que delegan en `src/algoritmos/correccionErrores.py` (mismo Hamming del Lab 2, aplicado en bloques de 4 bits)
- Payloads AUTH/WITHDRAW/ERROR/LOGOUT → `src/data/banking.py`

### 3. Cliente y servidor
- Nodo ATM (cliente) → `src/endpoints/client.py`
- Nodo servidor bancario → `src/endpoints/server.py`
- Ambos usan `src/net/sockets_utils.py` para hablar con su router gateway.

### 4. Concurrencia
- Hilos de routing/forwarding en paralelo → definidos en `src/node.py` (ej. `threading.Thread` para `control` y otro para `data`).

### 5. Pruebas (Tailscale)
- `tests/` para unit tests locales antes de probar en red.
- `logs/nodo_<id>.log` para verificar convergencia y ruta óptima durante las pruebas reales con las otras parejas.

### 6. Repo y entregables
- `README.md` con instalación/uso (requerido por el enunciado).
- `docs/reporte.pdf` con el reporte escrito final.
- Repo ya inicializado en `github.com/Brariv/Lab3-Enrutamiento`.
