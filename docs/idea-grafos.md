# Modelo de rompecabezas con grafos

La solución propone representar el rompecabezas como un grafo: cada pieza es un nodo y cada unión válida entre dos piezas es una arista. Esto permite modelar rompecabezas de distintas formas sin asumir una grilla fija de posiciones `(x, y)`.

## Idea central

| Elemento real | Representación en grafo |
| --- | --- |
| Rompecabezas | Nodo `Puzzle` |
| Pieza | Nodo `Piece` |
| Unión entre piezas | Relación `CONNECTS` |
| Unión física identificable | Propiedad `conector_id` de la relación |
| Flechita o letra visible | Propiedad `estilo` de la relación |
| Pieza faltante | `Piece.disponible = false` |
| Fragmento armable | Componente conectado del grafo disponible |

Ejemplo conceptual:

```text
Pieza 1 --[C001 / a]-- Pieza 3
Pieza 1 --[C002 / b]-- Pieza 5
Pieza 3 --[C003 / c]-- Pieza 7
```

Instrucciones generadas:

```text
Conectar la pieza 1 con la pieza 3 juntando las flechitas "a".
Conectar la pieza 1 con la pieza 5 juntando las flechitas "b".
Conectar la pieza 3 con la pieza 7 juntando las flechitas "c".
```

## Por qué no usar coordenadas fijas

No todos los rompecabezas tienen una forma rectangular o una estructura que pueda representarse naturalmente como una grilla. Por eso, en lugar de guardar posiciones absolutas como `pos_x` y `pos_y`, el modelo guarda **posiciones relativas**.

Una pieza queda ubicada por sus conexiones con otras piezas:

```text
La pieza 3 está conectada con:
- pieza 1 por el conector "a"
- pieza 7 por el conector "c"
- pieza 8 por el conector "d"
```

Esta posición topológica es más flexible y permite representar rompecabezas con formas irregulares.

## Modelo de datos propuesto

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

(:Piece)-[:BELONGS_TO]->(:Puzzle)

(:Piece)-[:CONNECTS {
  conector_id: "C001",
  estilo: "a"
}]-(:Piece)
```

## Datos necesarios a capturar

El modelo debe guardar únicamente los datos necesarios para identificar el rompecabezas, saber qué piezas están disponibles y conocer cómo se conectan entre sí.

### Datos del rompecabezas

| Campo | Uso |
| --- | --- |
| `puzzle_id` | Identificador único del rompecabezas. |
| `tema` | Describe la temática o imagen del rompecabezas. |
| `marca` | Marca del rompecabezas, si se conoce. |
| `material` | Material principal, por ejemplo cartón, madera o plástico. |
| `total_piezas` | Cantidad total de piezas esperadas. |

### Datos de cada pieza

| Campo | Uso |
| --- | --- |
| `piece_id` | Identificador único de la pieza. |
| `numero` | Número visible o asignado a la pieza. |
| `disponible` | Indica si la pieza existe físicamente o si está faltante. |

### Datos de cada conexión

| Campo | Uso |
| --- | --- |
| `pieza_origen` | Pieza desde la cual se registra la conexión. |
| `pieza_destino` | Pieza con la que se conecta. |
| `conector_id` | Identificador único de la unión dentro del rompecabezas. |
| `estilo` | Flechita o letra visible usada por la persona para conectar las piezas. |

Ejemplo:

```text
pieza_origen: 1
pieza_destino: 3
conector_id: C001
estilo: a
```

Instrucción generada:

```text
Conectar la pieza 1 con la pieza 3 juntando las flechitas "a".
```

El modelo puede aceptar más propiedades descriptivas, como color, forma, tamaño o notas, pero el algoritmo no depende de ellas. Para resolver el problema, lo esencial es conocer las piezas disponibles y las conexiones entre ellas.

### Identificadores de conexión

Para evitar ambigüedad, cada conexión debe tener un `conector_id` único dentro del rompecabezas.

Ejemplo:

```text
C001 identifica únicamente la unión entre la pieza 1 y la pieza 3.
C002 identifica únicamente la unión entre la pieza 1 y la pieza 5.
C003 identifica únicamente la unión entre la pieza 3 y la pieza 7.
```

La flechita o letra que ve la persona puede guardarse aparte en `estilo`.

```text
conector_id: identificador único para la base de datos y el algoritmo.
estilo: letra o flechita escrita físicamente en las piezas.
```

Esto permite generar instrucciones claras sin depender de que las letras visibles sean únicas.

```text
Conectar la pieza 1 con la pieza 3 juntando las flechitas "a".
```

Si se quiere máxima claridad en la demo, se recomienda que el `estilo` también sea único. Sin embargo, el campo obligatorio para evitar confusión en la base de datos debe ser `conector_id`.

### Campos opcionales para mejorar el modelo

Si el rompecabezas tiene información adicional, se podrían agregar propiedades opcionales a la relación:

```cypher
(:Piece)-[:CONNECTS {
  conector_id: "C001",
  estilo: "a",
  descripcion: "flechita a",
  orientacion_relativa: "opcional",
  notas: "opcional"
}]-(:Piece)
```

Estos campos no son obligatorios porque el modelo debe funcionar para distintos tipos de rompecabezas.

## Una pieza puede tener muchas conexiones

El modelo permite que una pieza tenga cualquier número de conexiones.

```text
Pieza 1
├── conecta con Pieza 3 por C001 / "a"
├── conecta con Pieza 5 por C002 / "b"
└── conecta con Pieza 8 por C003 / "c"
```

Esto es importante porque una pieza puede conectarse con varias piezas diferentes. En términos de grafos, una pieza puede tener grado `0`, `1`, `2`, `3` o más.

## Algoritmo de armado

El algoritmo puede usar BFS para recorrer el grafo desde cualquier pieza inicial y generar instrucciones de armado.

### Entrada

- `puzzle_id`: rompecabezas que se quiere armar.
- `pieza_inicial`: número o identificador de la pieza desde donde se desea empezar.

### Salida

- Lista ordenada de instrucciones para armar el rompecabezas.
- Avisos si hay piezas faltantes.
- Avisos si el rompecabezas queda dividido en varios fragmentos.

### Lógica general

```text
1. Cargar las piezas disponibles del rompecabezas.
2. Empezar BFS desde la pieza inicial indicada.
3. Por cada conexión encontrada:
   - si la pieza vecina está disponible y no fue visitada:
     - generar instrucción de conexión
     - agregar la pieza vecina a la cola
   - si la pieza vecina no está disponible:
     - reportar que esa conexión no puede realizarse porque falta una pieza
4. Si la cola queda vacía pero todavía hay piezas disponibles sin visitar:
   - avisar que el rompecabezas está fragmentado
   - elegir otra pieza disponible no visitada
   - iniciar un nuevo BFS desde esa pieza
5. Terminar cuando todas las piezas disponibles hayan sido visitadas.
```

## Manejo de piezas faltantes

Si una pieza está marcada como no disponible, el algoritmo no debe intentar usarla para continuar el armado.

Ejemplo:

```text
Pieza 1 --[a]-- Pieza 3 --[b]-- Pieza 5
```

Si la pieza 3 falta, entonces la pieza 1 y la pieza 5 no quedan conectadas dentro del grafo disponible. El algoritmo debe reportar que el rompecabezas se fragmentó.

Mensaje esperado:

```text
No se puede conectar con la pieza 3 porque no está disponible.
El rompecabezas quedó fragmentado. Iniciando nuevo fragmento desde la pieza 5.
```

## Selección del siguiente fragmento

Si el recorrido BFS termina y todavía existen piezas disponibles sin visitar, significa que el rompecabezas quedó dividido en más de un componente conectado.

En ese caso, el algoritmo debe iniciar un nuevo fragmento desde la pieza disponible no visitada con menor número.

Ejemplo:

```text
Piezas disponibles sin visitar: 2, 8, 10
Siguiente fragmento: pieza 2
```

No se recomienda elegir una pieza aleatoria porque haría que las instrucciones cambien en cada ejecución. Elegir la pieza con menor número hace que el algoritmo sea determinista, más fácil de probar y más claro durante la demostración.

Mensaje esperado:

```text
El rompecabezas quedó fragmentado.
No hay más conexiones disponibles desde el fragmento actual.
Iniciando nuevo fragmento desde la pieza 2.
```

## Justificación de base de datos de grafos

Una base de datos de grafos es adecuada porque el problema está definido principalmente por relaciones entre piezas. La operación central no es buscar filas aisladas, sino recorrer conexiones.

Ventajas:

- Representa naturalmente piezas y conexiones.
- Permite que una pieza tenga múltiples conexiones.
- Facilita recorrer vecinos desde una pieza inicial.
- Facilita detectar fragmentos o componentes desconectados.
- Evita forzar una estructura rígida como una grilla.

## Estrategia de implementación

La base de datos puede usarse como fuente de verdad del modelo, mientras que Python puede encargarse de ejecutar el algoritmo de armado.

```text
Neo4j / Cypher:
- guarda rompecabezas, piezas y conexiones
- permite consultar vecinos y piezas disponibles
- mantiene el modelo persistente

Python:
- carga el grafo desde la base de datos
- ejecuta BFS
- detecta fragmentos desconectados
- genera instrucciones legibles para la demo
```

Esta separación da flexibilidad: Neo4j representa naturalmente las relaciones, pero Python permite implementar y modificar el algoritmo con mayor facilidad.

## Consultas Cypher necesarias

### Crear un rompecabezas

```cypher
CREATE (:Puzzle {
  puzzle_id: "P001",
  marca: "Ravensburger",
  tema: "Paisaje",
  material: "Cartón",
  total_piezas: 100
});
```

### Crear una pieza

```cypher
MATCH (p:Puzzle {puzzle_id: "P001"})
CREATE (piece:Piece {
  piece_id: "P001-1",
  numero: 1,
  disponible: true
})
CREATE (piece)-[:BELONGS_TO]->(p);
```

### Crear una conexión entre dos piezas

```cypher
MATCH (a:Piece {piece_id: "P001-1"})
MATCH (b:Piece {piece_id: "P001-3"})
CREATE (a)-[:CONNECTS {
  conector_id: "C001",
  estilo: "a"
}]-(b);
```

### Obtener todas las piezas disponibles de un rompecabezas

```cypher
MATCH (piece:Piece)-[:BELONGS_TO]->(:Puzzle {puzzle_id: "P001"})
WHERE piece.disponible = true
RETURN piece.piece_id AS piece_id,
       piece.numero AS numero
ORDER BY piece.numero;
```

### Obtener todas las conexiones de piezas disponibles

Esta consulta sirve para cargar el grafo en Python.

```cypher
MATCH (a:Piece)-[r:CONNECTS]-(b:Piece)
MATCH (a)-[:BELONGS_TO]->(:Puzzle {puzzle_id: "P001"})
MATCH (b)-[:BELONGS_TO]->(:Puzzle {puzzle_id: "P001"})
WHERE a.disponible = true
  AND b.disponible = true
RETURN a.numero AS pieza_a,
       b.numero AS pieza_b,
       r.conector_id AS conector_id,
       r.estilo AS estilo
ORDER BY a.numero, b.numero;
```

### Obtener vecinos de una pieza específica

Esta consulta sirve si el BFS se ejecuta consultando la base de datos paso a paso.

```cypher
MATCH (actual:Piece {piece_id: "P001-1"})-[r:CONNECTS]-(vecina:Piece)
WHERE vecina.disponible = true
RETURN vecina.piece_id AS piece_id,
       vecina.numero AS numero,
       r.conector_id AS conector_id,
       r.estilo AS estilo
ORDER BY vecina.numero;
```

### Obtener piezas faltantes

```cypher
MATCH (piece:Piece)-[:BELONGS_TO]->(:Puzzle {puzzle_id: "P001"})
WHERE piece.disponible = false
RETURN piece.piece_id AS piece_id,
       piece.numero AS numero
ORDER BY piece.numero;
```

## Opción recomendada para el algoritmo

Para la demo, se recomienda cargar el grafo completo desde Neo4j hacia Python y ejecutar BFS en memoria.

Ventajas:

- El algoritmo queda más fácil de escribir y explicar.
- Se evita hacer una consulta a la base de datos por cada paso del recorrido.
- Es más simple detectar componentes desconectados.
- Permite cambiar la lógica del recorrido sin modificar el modelo de datos.

Flujo recomendado:

```text
1. Consultar piezas disponibles.
2. Consultar conexiones entre piezas disponibles.
3. Construir una lista de adyacencia en Python.
4. Ejecutar BFS desde la pieza inicial.
5. Si quedan piezas disponibles no visitadas, iniciar otro BFS desde la de menor número.
6. Generar instrucciones finales.
```

## Ingesta manual de datos

Como los datos del rompecabezas se van a capturar manualmente, conviene usar un formato intermedio simple antes de insertarlos en Neo4j. La recomendación es usar archivos CSV porque son fáciles de llenar en Excel, Google Sheets o LibreOffice Calc.

La idea es separar la ingesta en tres archivos:

```text
puzzles.csv
pieces.csv
connections.csv
```

### `puzzles.csv`

```csv
puzzle_id,marca,tema,material,total_piezas
P001,Ravensburger,Paisaje,Cartón,10
```

### `pieces.csv`

```csv
puzzle_id,numero,disponible
P001,1,true
P001,2,true
P001,3,false
P001,4,true
```

El `piece_id` no debe llenarse manualmente. El script de ingesta puede generarlo automáticamente usando el `puzzle_id` y el número de pieza.

Ejemplo:

```text
puzzle_id: P001
numero: 4
piece_id generado: P001-4
```

### `connections.csv`

```csv
puzzle_id,pieza_a,pieza_b,estilo
P001,1,3,a
P001,1,4,b
P001,2,4,c
```

El `conector_id` tampoco debe llenarse manualmente. El script de ingesta puede generarlo automáticamente por cada conexión.

Ejemplo:

```text
Primera conexión de P001: C001
Segunda conexión de P001: C002
Tercera conexión de P001: C003
```

No se recomienda depender de los IDs internos de Neo4j para identificar piezas o conexiones en el algoritmo. Esos IDs son útiles internamente para la base de datos, pero no son buenos identificadores de dominio porque pueden cambiar si se exportan, eliminan o recrean datos.

La recomendación es:

```text
Manual:
- puzzle_id
- numero de pieza
- disponible
- pieza_a
- pieza_b
- estilo

Automático:
- piece_id
- conector_id
```

Con esta estructura, la captura manual queda clara:

1. Registrar el rompecabezas en `puzzles.csv`.
2. Registrar todas las piezas en `pieces.csv`.
3. Marcar con `false` las piezas faltantes.
4. Registrar las conexiones conocidas en `connections.csv`.
5. Ejecutar un script de carga que genere los IDs faltantes, lea los CSV e inserte los datos en Neo4j.

### Validaciones recomendadas antes de insertar

Antes de cargar los datos a Neo4j, el script de ingesta debería validar:

- que no haya piezas repetidas dentro del mismo rompecabezas;
- que cada conexión use piezas existentes;
- que `conector_id` no se repita dentro del mismo rompecabezas;
- que no haya conexiones duplicadas entre las mismas piezas con el mismo conector;
- que los campos obligatorios no estén vacíos.

Esto reduce errores durante la demo y evita que el algoritmo falle por datos mal capturados.

### Flujo recomendado de ingesta

```text
Datos físicos del rompecabezas
        ↓
CSV llenados manualmente
        ↓
Script Python de validación
        ↓
Inserción en Neo4j con Cypher
        ↓
Script Python de armado usando BFS
```

Separar la captura manual de la inserción en base de datos hace que el proceso sea más fácil de revisar, corregir y repetir.

## Formato de instrucciones para la demo

Las instrucciones deben ser simples, ordenadas y fáciles de seguir físicamente durante la presentación.

### Inicio

```text
Iniciando armado del rompecabezas P001 desde la pieza 4.
```

### Conexión normal

```text
Paso 1: conectar la pieza 4 con la pieza 7 juntando las flechitas "a".
Paso 2: conectar la pieza 4 con la pieza 2 juntando las flechitas "b".
Paso 3: conectar la pieza 7 con la pieza 9 juntando las flechitas "c".
```

Cada instrucción debe indicar:

- número de paso;
- pieza ya alcanzada por el recorrido;
- pieza nueva que se debe conectar;
- flechitas o conector que permite unirlas.

### Pieza faltante

Si una conexión apunta a una pieza marcada como no disponible, se debe mostrar un aviso.

```text
Aviso: la pieza 3 no está disponible. No se puede realizar la conexión juntando las flechitas "d" (C004).
```

### Fragmento desconectado

Si el BFS termina y todavía quedan piezas disponibles sin visitar, el algoritmo debe indicar que se inicia otro fragmento.

```text
El rompecabezas quedó fragmentado.
No hay más conexiones disponibles desde el fragmento actual.
Iniciando nuevo fragmento desde la pieza 10.
```

### Resumen final

Al terminar, se recomienda mostrar un resumen para que la demo sea clara.

```text
Armado finalizado.
Piezas disponibles armadas: 8
Piezas faltantes detectadas: 2
Fragmentos generados: 2
```

Este formato ayuda a demostrar que el algoritmo no solo recorre el grafo, sino que también comunica claramente qué debe hacer una persona para armar el rompecabezas.

## Dataset de ejemplo para la demo

Para demostrar el funcionamiento completo, se propone usar un dataset mínimo de 15 piezas. Este tamaño permite mostrar un caso suficientemente interesante sin volver la demostración demasiado larga.

El dataset debe incluir:

- una pieza inicial que no sea la pieza 1;
- piezas con varias conexiones;
- al menos una pieza faltante;
- al menos dos fragmentos conectados;
- continuación determinista desde la pieza disponible no visitada con menor número.

### Piezas

```csv
puzzle_id,numero,disponible
P001,1,true
P001,2,true
P001,3,true
P001,4,true
P001,5,true
P001,6,false
P001,7,true
P001,8,true
P001,9,true
P001,10,true
P001,11,true
P001,12,false
P001,13,true
P001,14,true
P001,15,true
```

### Conexiones

```csv
puzzle_id,pieza_a,pieza_b,estilo
P001,1,2,a
P001,2,3,b
P001,2,4,c
P001,4,5,d
P001,5,6,e
P001,3,7,f
P001,7,8,g
P001,8,9,h
P001,9,10,i
P001,10,11,j
P001,11,12,k
P001,13,14,l
P001,14,15,m
```

### Comportamiento esperado

Si el algoritmo inicia desde la pieza 4:

```text
Iniciando armado del rompecabezas P001 desde la pieza 4.

Paso 1: conectar la pieza 4 con la pieza 2 juntando las flechitas "c" (C003).
Paso 2: conectar la pieza 4 con la pieza 5 juntando las flechitas "d" (C004).
Paso 3: conectar la pieza 2 con la pieza 1 juntando las flechitas "a" (C001).
Paso 4: conectar la pieza 2 con la pieza 3 juntando las flechitas "b" (C002).
Aviso: la pieza 6 no está disponible. No se puede realizar la conexión juntando las flechitas "e" (C005).
Paso 5: conectar la pieza 3 con la pieza 7 juntando las flechitas "f" (C006).
Paso 6: conectar la pieza 7 con la pieza 8 juntando las flechitas "g" (C007).
Paso 7: conectar la pieza 8 con la pieza 9 juntando las flechitas "h" (C008).
Paso 8: conectar la pieza 9 con la pieza 10 juntando las flechitas "i" (C009).
Paso 9: conectar la pieza 10 con la pieza 11 juntando las flechitas "j" (C010).
Aviso: la pieza 12 no está disponible. No se puede realizar la conexión juntando las flechitas "k" (C011).

El rompecabezas quedó fragmentado.
No hay más conexiones disponibles desde el fragmento actual.
Iniciando nuevo fragmento desde la pieza 13.

Paso 10: conectar la pieza 13 con la pieza 14 juntando las flechitas "l" (C012).
Paso 11: conectar la pieza 14 con la pieza 15 juntando las flechitas "m" (C013).

Armado finalizado.
Piezas disponibles armadas: 13
Piezas faltantes detectadas: 2
Fragmentos generados: 2
```

Este dataset demuestra el caso completo: recorrido desde una pieza inicial arbitraria, múltiples conexiones por pieza, piezas faltantes y fragmentación del grafo.

## Pendientes por definir

- Implementar el script de ingesta desde CSV hacia Neo4j.
- Implementar el script en Python que carga el grafo desde Neo4j y ejecuta BFS.
