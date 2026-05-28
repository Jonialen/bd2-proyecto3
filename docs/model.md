**Nodos:**

```cypher
(:Puzzle {
  puzzle_id: "P001",
  marca: "Ravensburger",
  tema: "Paisaje",
  material: "Cartón",
  total_piezas: 100
})

(:Piece {
  piece_id: "P001-42",
  numero: 42,
  disponible: true
})

```

**Relaciones:**

```cypher
(:Piece)-[:CONNECTS {
  conector_id: "a"
}]->(:Piece)

(:Piece)-[:BELONGS_TO]->(:Puzzle)

```
