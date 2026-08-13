# Lab 3 — Protocolos de Enrutamiento — Checklist

Estado actual del repo: vacío (solo `README.md` y `.gitignore`, sin código). Este documento es la guía punto por punto para implementarlo desde cero, basada en el PDF del laboratorio.

## 0. Antes de programar

- [ ] Confirmar grupo de 2 (mismos de Lab 2) y la topología de 3 parejas (6 nodos) que les toca.
- [ ] Elegir lenguaje/stack (Python, Node, Java, etc.) y definir cómo se ejecuta fácil (`venv`, `npm run`, `Makefile`, `.jar`).
- [ ] Acordar con las otras 2 parejas el formato exacto de mensajes JSON (LSA, HELLO, datos) para que haya interoperabilidad.
- [ ] Cada nodo necesita: su propia IP/puerto (Tailscale luego), lista de vecinos y costos iniciales — normalmente vía archivo de config.

## 1. Plano de control (Link State) — 3.1

- [ ] **Descubrimiento de vecinos**: al iniciar, el nodo lee su config y sabe quiénes son sus vecinos.
- [ ] **Paquetes HELLO**: enviar/recibir HELLO a cada vecino para confirmar que el enlace está activo.
- [ ] **Recepción de costos de enlace**: cada nodo conoce el costo hacia cada vecino (dado en la config/topología).
- [ ] **Construcción del LSA** (Link State Advertisement) con el formato acordado, ej:
  ```json
  { "type": "LSA", "origin": self_ip, "seq": seq, "links": links, "from": self_ip }
  ```
- [ ] **Flooding**: reenviar el LSA recibido a todos los vecinos excepto por donde llegó (evitar loops usando `seq` por origen).
- [ ] **Construcción del grafo de la red** a partir de todos los LSA recibidos.
- [ ] **Cálculo de rutas más cortas** (Dijkstra) sobre ese grafo.
- [ ] **Generar `nodo_tabla_enrutamiento.csv`** con destino → siguiente salto / IP / puerto, para que lo use el plano de datos.
- [ ] Correr esto en un **hilo/proceso separado** del forwarding (routing y forwarding en paralelo).

## 2. Plano de datos y capas — 3.2

- [ ] Definir formato de mensaje de datos serializado: `{nodo_origen, nodo_destino, mensaje}`.
- [ ] **Capa de red**: al recibir un mensaje, extraer `nodo_destino`, buscarlo en `nodo_tabla_enrutamiento.csv`, obtener IP/puerto del siguiente salto, y reenviar por socket.
- [ ] **Capa de enlace (Hamming 7,4)** — reutilizar del Lab 2 — aplicada solo cuando ya se calcularon las tablas de ruteo. Flujo completo por mensaje:
  1. [ ] Recibir cadena de bits.
  2. [ ] Detectar y corregir errores (Hamming 7,4) sobre todos los bits.
  3. [ ] Extraer los bits de datos.
  4. [ ] Deserializar los bits del destino.
  5. [ ] Consultar tabla de ruteo.
  6. [ ] Abrir conexión por socket según IP/puerto obtenidos.
  7. [ ] Serializar los bits del destino.
  8. [ ] Aplicar Hamming 7,4 a todos los bits salientes.
  9. [ ] Enviar los bits por el socket.

## 3. Cliente y servidor

- [ ] Definir qué nodo es cliente y cuál es servidor (no son routers).
- [ ] Cliente ↔ su nodo router (gateway) vía sockets.
- [ ] Servidor ↔ su nodo router (gateway) vía sockets.

## 4. Concurrencia

- [ ] Cada nodo corre routing (control) y forwarding (datos) simultáneamente: hilos, procesos o async, con timeouts donde aplique.
- [ ] Verificar que el algoritmo converge (tablas estables) antes de mandar mensajes de datos.

## 5. Pruebas — 3.3

- [ ] Instalar y configurar Tailscale (cuenta personal de Google), crear/unirse a la red de 6 usuarios (3 parejas).
- [ ] Probar que el LSA + flooding + Dijkstra funciona entre las 3 implementaciones distintas (interoperabilidad de formato JSON).
- [ ] Probar envío de mensaje cliente → servidor a través de la ruta óptima calculada.
- [ ] Verificar que los mensajes efectivamente toman la ruta de menor costo.

## 6. Repositorio y entregables

- [ ] Código subido y organizado en el repo (`Brariv/Lab3-Enrutamiento`), con README explicando instalación/uso (requerimientos, cómo correr cada nodo).
- [ ] Reporte en PDF: encabezado, descripción de la práctica, descripción de algoritmos e implementación, resultados, discusión, conclusiones + referencias.
- [ ] Entregar en Canvas: (1) reporte PDF, (2) código (zip/rar si aplica), (3) link al repositorio.

## Rúbrica (referencia rápida)

| Elemento | % |
|---|---|
| Código — limpieza/documentación | 5% |
| Código — implementación de algoritmos | 70% |
| Reporte — encabezado/formato/descripción | 2.5% |
| Reporte — descripción de algoritmos | 10% |
| Reporte — resultados | 5% |
| Reporte — discusión | 5% |
| Reporte — conclusiones/referencias | 2.5% |

Nota: una inasistencia injustificada anula la nota del laboratorio.
