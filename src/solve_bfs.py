"""Generate deterministic puzzle assembly instructions with BFS."""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass

from neo4j import GraphDatabase

from config import load_config


@dataclass(frozen=True)
class PieceInfo:
    numero: int
    disponible: bool


@dataclass(frozen=True)
class Neighbor:
    numero: int
    disponible: bool
    conector_id: str
    etiqueta_visible: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Solve a puzzle graph with deterministic BFS.")
    parser.add_argument("--puzzle-id", default="P001", help="Puzzle identifier to solve. Default: P001")
    parser.add_argument("--start", type=int, required=True, help="Available piece number to start from.")
    return parser.parse_args()


def load_graph(puzzle_id: str) -> tuple[dict[int, PieceInfo], dict[int, list[Neighbor]]]:
    config = load_config()
    with GraphDatabase.driver(config.uri, auth=(config.user, config.password)) as driver:
        driver.verify_connectivity()
        with driver.session() as session:
            piece_rows = session.run(
                """
                MATCH (pc:Piece)-[:BELONGS_TO]->(:Puzzle {puzzle_id: $puzzle_id})
                RETURN pc.numero AS numero, pc.disponible AS disponible
                ORDER BY pc.numero
                """,
                puzzle_id=puzzle_id,
            )
            pieces = {row["numero"]: PieceInfo(row["numero"], row["disponible"]) for row in piece_rows}

            connection_rows = list(session.run(
                """
                MATCH (a:Piece)-[c:CONNECTS]-(b:Piece),
                      (a)-[:BELONGS_TO]->(:Puzzle {puzzle_id: $puzzle_id}),
                      (b)-[:BELONGS_TO]->(:Puzzle {puzzle_id: $puzzle_id})
                RETURN a.numero AS pieza_a,
                       a.disponible AS disponible_a,
                       b.numero AS pieza_b,
                       b.disponible AS disponible_b,
                       c.conector_id AS conector_id,
                       c.etiqueta_visible AS etiqueta_visible
                """,
                puzzle_id=puzzle_id,
            ))

    adjacency = {numero: [] for numero in pieces}
    seen_relationships: set[tuple[int, int, str]] = set()
    for row in connection_rows:
        a = row["pieza_a"]
        b = row["pieza_b"]
        conector_id = row["conector_id"]
        key = (min(a, b), max(a, b), conector_id)
        if key in seen_relationships:
            continue
        seen_relationships.add(key)
        adjacency[a].append(Neighbor(b, row["disponible_b"], conector_id, row["etiqueta_visible"]))
        adjacency[b].append(Neighbor(a, row["disponible_a"], conector_id, row["etiqueta_visible"]))

    for neighbors in adjacency.values():
        neighbors.sort(key=lambda neighbor: (neighbor.numero, neighbor.conector_id))
    return pieces, adjacency


def solve(puzzle_id: str, start: int, pieces: dict[int, PieceInfo], adjacency: dict[int, list[Neighbor]]) -> None:
    if start not in pieces:
        raise SystemExit(f"Error: piece {start} does not exist in puzzle {puzzle_id}.")
    if not pieces[start].disponible:
        raise SystemExit(f"Error: piece {start} is not available and cannot be used as the start.")

    available = {numero for numero, piece in pieces.items() if piece.disponible}
    visited: set[int] = set()
    missing_warned: set[int] = set()
    fragments = 0
    step = 1
    current_start = start

    print(f"Iniciando armado del rompecabezas {puzzle_id} desde la pieza {start}.")

    while len(visited) < len(available):
        fragments += 1
        queue: deque[int] = deque([current_start])
        visited.add(current_start)

        while queue:
            current = queue.popleft()
            for neighbor in adjacency.get(current, []):
                if not neighbor.disponible:
                    if neighbor.numero not in missing_warned:
                        missing_warned.add(neighbor.numero)
                        print(
                            f'Aviso: la pieza {neighbor.numero} no está disponible. '
                            f'No se puede realizar la conexión con la marca visible "{neighbor.etiqueta_visible}" '
                            f'({neighbor.conector_id}).'
                        )
                    continue
                if neighbor.numero in visited:
                    continue
                visited.add(neighbor.numero)
                queue.append(neighbor.numero)
                print(
                    f'Paso {step}: conectar la pieza {current} con la pieza {neighbor.numero} '
                    f'usando la marca visible "{neighbor.etiqueta_visible}" ({neighbor.conector_id}).'
                )
                step += 1

        remaining = sorted(available - visited)
        if remaining:
            current_start = remaining[0]
            print()
            print("El rompecabezas quedó fragmentado.")
            print("No hay más conexiones disponibles desde el fragmento actual.")
            print(f"Iniciando nuevo fragmento desde la pieza {current_start}.")
            print()

    print()
    print("Armado finalizado.")
    print(f"Piezas disponibles armadas: {len(visited)}")
    print(f"Piezas faltantes detectadas: {len(missing_warned)}")
    print(f"Fragmentos generados: {fragments}")


def main() -> None:
    args = parse_args()
    pieces, adjacency = load_graph(args.puzzle_id)
    if not pieces:
        raise SystemExit(f"Error: puzzle {args.puzzle_id} was not found or has no pieces.")
    solve(args.puzzle_id, args.start, pieces, adjacency)


if __name__ == "__main__":
    main()
