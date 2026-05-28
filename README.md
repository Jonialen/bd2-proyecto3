# Puzzle graph demo with Neo4j and Python

This project models a puzzle as a graph: pieces are nodes, physical matches are `CONNECTS` relationships, and missing pieces are stored with `disponible=false`. The demo loads a 15-piece CSV dataset into Neo4j and prints deterministic BFS assembly instructions.

## Quick path

1. Start Neo4j:
   ```bash
   docker compose up -d
   ```
2. Install Python dependencies with uv:
   ```bash
   uv sync
   ```
3. Load the CSV dataset:
   ```bash
   uv run python src/ingest.py
   ```
4. Generate assembly instructions from piece 4:
   ```bash
   uv run python src/solve_bfs.py --puzzle-id P001 --start 4
   ```

Neo4j Browser is available at <http://localhost:7474> with user `neo4j` and password `password`.

## Configuration

The scripts use local defaults that match `docker-compose.yml`.

| Variable | Default |
|---|---|
| `NEO4J_URI` | `bolt://localhost:7687` |
| `NEO4J_USER` | `neo4j` |
| `NEO4J_PASSWORD` | `password` |

## CSV files

Manual CSV entry does not require generated domain IDs.

| File | Purpose |
|---|---|
| `data/puzzles.csv` | Puzzle metadata: `puzzle_id,marca,tema,material,total_piezas` |
| `data/pieces.csv` | Piece availability: `puzzle_id,numero,disponible` |
| `data/connections.csv` | Physical matches: `puzzle_id,pieza_a,pieza_b,estilo` |

During ingest, the script generates:

- `piece_id` as `{puzzle_id}-{numero}`, for example `P001-4`.
- `conector_id` as `C001`, `C002`, ... in CSV connection order per puzzle.
- `estilo` stores the visible arrow/letter used to join each physical match.

## Demo behavior

The included `P001` dataset has 15 pieces. Pieces `6` and `12` are unavailable, and pieces `13-15` form a separate available fragment.

When solving from piece `4`, the output demonstrates:

- arbitrary start piece support;
- deterministic neighbor order by `(neighbor number, conector_id)`;
- warnings for missing pieces;
- continuation from the smallest unvisited available piece when the graph is fragmented;
- a final summary with assembled pieces, missing pieces, and fragment count.

Expected final summary:

```text
Armado finalizado.
Piezas disponibles armadas: 13
Piezas faltantes detectadas: 2
Fragmentos generados: 2
```

## Useful Neo4j checks

Run these in Neo4j Browser after ingest:

```cypher
MATCH (p:Puzzle) RETURN count(p) AS puzzles;
MATCH (pc:Piece) RETURN count(pc) AS pieces;
MATCH ()-[c:CONNECTS]-() RETURN count(c) / 2 AS connections;
```
