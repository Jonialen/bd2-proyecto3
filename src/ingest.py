"""Load puzzle CSV data into Neo4j with deterministic domain IDs."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from neo4j import GraphDatabase

from config import load_config


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


class ValidationError(Exception):
    """Raised when a CSV row violates the manual data contract."""


@dataclass(frozen=True)
class Puzzle:
    puzzle_id: str
    marca: str
    tema: str
    material: str
    total_piezas: int


@dataclass(frozen=True)
class Piece:
    puzzle_id: str
    numero: int
    disponible: bool

    @property
    def piece_id(self) -> str:
        return f"{self.puzzle_id}-{self.numero}"


@dataclass(frozen=True)
class Connection:
    puzzle_id: str
    pieza_a: int
    pieza_b: int
    etiqueta_visible: str
    conector_id: str


def required(row: dict[str, str], field: str, source: str, line_number: int) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        raise ValidationError(f"{source}:{line_number}: field '{field}' is required")
    return value


def parse_positive_int(value: str, field: str, source: str, line_number: int) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValidationError(f"{source}:{line_number}: field '{field}' must be an integer") from exc
    if parsed <= 0:
        raise ValidationError(f"{source}:{line_number}: field '{field}' must be positive")
    return parsed


def parse_bool(value: str, source: str, line_number: int) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y", "si", "sí"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise ValidationError(f"{source}:{line_number}: field 'disponible' must be true or false")


def read_csv(path: Path) -> Iterable[tuple[int, dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for line_number, row in enumerate(reader, start=2):
            yield line_number, row


def load_puzzles() -> list[Puzzle]:
    puzzles: list[Puzzle] = []
    seen: set[str] = set()
    source = "data/puzzles.csv"
    for line_number, row in read_csv(DATA_DIR / "puzzles.csv"):
        puzzle_id = required(row, "puzzle_id", source, line_number)
        if puzzle_id in seen:
            raise ValidationError(f"{source}:{line_number}: duplicate puzzle_id '{puzzle_id}'")
        seen.add(puzzle_id)
        puzzles.append(
            Puzzle(
                puzzle_id=puzzle_id,
                marca=required(row, "marca", source, line_number),
                tema=required(row, "tema", source, line_number),
                material=required(row, "material", source, line_number),
                total_piezas=parse_positive_int(
                    required(row, "total_piezas", source, line_number),
                    "total_piezas",
                    source,
                    line_number,
                ),
            )
        )
    return puzzles


def load_pieces(valid_puzzles: set[str]) -> list[Piece]:
    pieces: list[Piece] = []
    seen: set[tuple[str, int]] = set()
    source = "data/pieces.csv"
    for line_number, row in read_csv(DATA_DIR / "pieces.csv"):
        puzzle_id = required(row, "puzzle_id", source, line_number)
        if puzzle_id not in valid_puzzles:
            raise ValidationError(f"{source}:{line_number}: unknown puzzle_id '{puzzle_id}'")
        numero = parse_positive_int(required(row, "numero", source, line_number), "numero", source, line_number)
        key = (puzzle_id, numero)
        if key in seen:
            raise ValidationError(f"{source}:{line_number}: duplicate piece {puzzle_id}-{numero}")
        seen.add(key)
        pieces.append(
            Piece(
                puzzle_id=puzzle_id,
                numero=numero,
                disponible=parse_bool(required(row, "disponible", source, line_number), source, line_number),
            )
        )
    return pieces


def load_connections(piece_keys: set[tuple[str, int]]) -> list[Connection]:
    connections: list[Connection] = []
    seen_edges: set[tuple[str, int, int]] = set()
    counters: dict[str, int] = {}
    source = "data/connections.csv"
    for line_number, row in read_csv(DATA_DIR / "connections.csv"):
        puzzle_id = required(row, "puzzle_id", source, line_number)
        pieza_a = parse_positive_int(required(row, "pieza_a", source, line_number), "pieza_a", source, line_number)
        pieza_b = parse_positive_int(required(row, "pieza_b", source, line_number), "pieza_b", source, line_number)
        if pieza_a == pieza_b:
            raise ValidationError(f"{source}:{line_number}: self-loop is not allowed for piece {pieza_a}")
        for numero in (pieza_a, pieza_b):
            if (puzzle_id, numero) not in piece_keys:
                raise ValidationError(f"{source}:{line_number}: unknown endpoint {puzzle_id}-{numero}")
        edge_key = (puzzle_id, min(pieza_a, pieza_b), max(pieza_a, pieza_b))
        if edge_key in seen_edges:
            raise ValidationError(f"{source}:{line_number}: duplicate connection {puzzle_id} {pieza_a}-{pieza_b}")
        seen_edges.add(edge_key)
        counters[puzzle_id] = counters.get(puzzle_id, 0) + 1
        connections.append(
            Connection(
                puzzle_id=puzzle_id,
                pieza_a=pieza_a,
                pieza_b=pieza_b,
                etiqueta_visible=required(row, "etiqueta_visible", source, line_number),
                conector_id=f"C{counters[puzzle_id]:03d}",
            )
        )
    return connections


def load_dataset() -> tuple[list[Puzzle], list[Piece], list[Connection]]:
    puzzles = load_puzzles()
    pieces = load_pieces({p.puzzle_id for p in puzzles})
    connections = load_connections({(p.puzzle_id, p.numero) for p in pieces})
    return puzzles, pieces, connections


def create_constraints(session) -> None:
    session.run("CREATE CONSTRAINT puzzle_id_unique IF NOT EXISTS FOR (p:Puzzle) REQUIRE p.puzzle_id IS UNIQUE")
    session.run("CREATE CONSTRAINT piece_id_unique IF NOT EXISTS FOR (pc:Piece) REQUIRE pc.piece_id IS UNIQUE")


def delete_puzzle(session, puzzle_id: str) -> None:
    session.run(
        """
        MATCH (p:Puzzle {puzzle_id: $puzzle_id})<-[:BELONGS_TO]-(pc:Piece)
        DETACH DELETE pc
        """,
        puzzle_id=puzzle_id,
    )
    session.run("MATCH (p:Puzzle {puzzle_id: $puzzle_id}) DELETE p", puzzle_id=puzzle_id)


def write_dataset(puzzles: list[Puzzle], pieces: list[Piece], connections: list[Connection]) -> None:
    config = load_config()
    with GraphDatabase.driver(config.uri, auth=(config.user, config.password)) as driver:
        driver.verify_connectivity()
        with driver.session() as session:
            create_constraints(session)
            for puzzle in puzzles:
                delete_puzzle(session, puzzle.puzzle_id)

            session.run(
                """
                UNWIND $puzzles AS row
                CREATE (:Puzzle {
                    puzzle_id: row.puzzle_id,
                    marca: row.marca,
                    tema: row.tema,
                    material: row.material,
                    total_piezas: row.total_piezas
                })
                """,
                puzzles=[p.__dict__ for p in puzzles],
            )
            session.run(
                """
                UNWIND $pieces AS row
                MATCH (p:Puzzle {puzzle_id: row.puzzle_id})
                CREATE (pc:Piece {
                    piece_id: row.piece_id,
                    numero: row.numero,
                    disponible: row.disponible
                })
                CREATE (pc)-[:BELONGS_TO]->(p)
                """,
                pieces=[{"piece_id": p.piece_id, **p.__dict__} for p in pieces],
            )
            session.run(
                """
                UNWIND $connections AS row
                MATCH (a:Piece {piece_id: row.piece_a_id})
                MATCH (b:Piece {piece_id: row.piece_b_id})
                CREATE (a)-[:CONNECTS {
                    conector_id: row.conector_id,
                    etiqueta_visible: row.etiqueta_visible
                }]->(b)
                """,
                connections=[
                    {
                        "piece_a_id": f"{c.puzzle_id}-{c.pieza_a}",
                        "piece_b_id": f"{c.puzzle_id}-{c.pieza_b}",
                        "conector_id": c.conector_id,
                        "etiqueta_visible": c.etiqueta_visible,
                    }
                    for c in connections
                ],
            )


def main() -> None:
    try:
        puzzles, pieces, connections = load_dataset()
        write_dataset(puzzles, pieces, connections)
    except ValidationError as exc:
        raise SystemExit(f"Validation error: {exc}") from exc

    print("Ingest completed.")
    print(f"Puzzles loaded: {len(puzzles)}")
    print(f"Pieces loaded: {len(pieces)}")
    print(f"Connections loaded: {len(connections)}")


if __name__ == "__main__":
    main()
