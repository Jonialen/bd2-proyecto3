**UNIVERSIDAD DEL VALLE DE GUATEMALA** **Facultad de Ingeniería** **Departamento de Ciencias de la Computación** **CC3089 Base de Datos 2** **Semestre 1 2026** 

Proyecto 03 - Elección de tecnologías de base de datos 

I. Modalidad y fecha de entrega 

* a) El proyecto deberá trabajarse en equipos (un equipo es la unión de dos grupos) y el entregable deberá tener los datos de todos los integrantes del equipo. 


* b) Los entregables deben cargarse en Canvas el jueves 28 de mayo, antes de las 17:00 horas. 



---

### II. 

Objetivo y descripción de la actividad 

El propósito de esta actividad es que los estudiantes desarrollen criterios técnicos para seleccionar el tipo de base de datos más adecuado en función de las características del problema a resolver. 

Cada equipo recibirá un rompecabezas. Si lo estiman útil, podrán pegarle pedazos pequeños de masking tape y escribir (suavemente) en estos. También podrán intercambiar rompecabezas con otros grupos, para acceder a insumos con otras características y poder comprender de forma más amplia el problema a resolver. 

Cada equipo deberá diseñar un modelo que permita guardar información de las piezas y de los rompecabezas, así como cualquier otra información que consideren relevante (tipo de rompecabezas, temática de la imagen del rompecabezas, marca, material, etc.).  Es importante que el modelo sea escalable. Luego, deberá seleccionar una base de datos adecuada (SQL o NoSQL), justificar su elección, implementar el modelo y poblar la base de datos con la información de los rompecabezas proporcionados. 

Finalmente, deberá desarrollar un algoritmo que, partiendo de una pieza (cualquiera), indique los pasos para armar el rompecabezas completo. Cada grupo deberá exponer su solución ante el docente. 

Es importante tener claro que la elección de tecnología de base de datos impactará en la dificultad de la solución, así como el tiempo requerido para completarla. 

---

### III. 

Instrucciones generales y observaciones 

* Analizar las características de los rompecabezas proporcionados. 


* Diseñar un modelo de datos que permita representar de manera efectiva las piezas, sus relaciones, los rompecabezas y demás información relevante. 


* Elegir una tecnología de base de datos adecuada (SQL o NoSQL) para almacenar dicha información, justificando la decisión. 


* Implementar el modelo en la base de datos seleccionada. 


* Desarrollar un programa (en el lenguaje de preferencia del equipo) que, dada una pieza inicial (cualquiera), indique los pasos para armar el rompecabezas completo (indicando en cada paso qué pieza sigue y con qué piezas debe ensamblarse). 


* Preparar una breve presentación para explicar su solución, incluyendo el diseño del modelo, la elección de la tecnología de base de datos y una demostración del algoritmo. 



---

### IV. 

Observaciones 

* El algoritmo deberá ser capaz de, si llegaran a faltar una o más piezas (y esto se registra en la base de datos), indicar los pasos para armar parcialmente el rompecabezas. 


* La solución a desarrollar deberá ser escalable. 


* La presentación final y la demostración no deberán exceder los 15 minutos. 


* Si un grupo se excede de los 20 minutos para exponer y llevar a cabo la demostración, se le penalizará restando una tercera parte de la nota obtenida. 


* Los estudiantes que no asistan a cualquiera de los dos días en los que se llevará a cabo del proyecto, no podrán reponerla y obtendrán una calificación de 0 puntos. 



---

V. Temas a reforzar 

* Modelado de datos. 


* Criterios de selección de tecnologías de base de datos. 


* Representación de estructuras complejas en bases de datos. 


* Desarrollo de algoritmos para resolución de problemas. 



---

### VI. 

Documentos a entregar 

Por equipo, se deberá entregar un archivo comprimido que contenga: 

* 1. Documento con evidencias (diagramas, capturas de pantalla, fotos de la actividad, etc.) que permitan a otros replicar la solución e incluya la justificación del modelo y de la tecnología elegida. 


* 2. Cualquier código fuente utilizado. 


* 3. Presentación utilizada para exponer en clase. 



---

### VII. 

Evaluación 

Rúbrica de evaluación: 

| Aspecto | Excelente | Bueno | Regular | Deficiente |
| --- | --- | --- | --- | --- |
| **1. Justificación de la elección de base de datos (10%)** | Justifica técnicamente la elección y la compara con otras alternativas. | Justifica la elección, aunque con comparación o criterios técnicos limitados. | Presenta una justificación básica, poco relacionada con el problema. | No justifica adecuadamente la tecnología seleccionada. |
| **2. Diseño del modelo de datos (20%)** | El modelo representa claramente rompecabezas, piezas, relaciones, posiciones y piezas faltantes. Es escalable. | El modelo representa la mayoría de elementos necesarios, con omisiones menores. | El modelo es parcialmente funcional, pero tiene omisiones importantes. | El modelo es incompleto, confuso o no permite resolver el problema. |
| **3. Implementación del modelo de datos (10%)** | Implementa correctamente el modelo en la base de datos seleccionada y lo puebla con datos válidos. | Implementa el modelo con detalles menores de consistencia u organización. | La implementación es parcial o presenta inconsistencias relevantes. | La implementación es mínima, incompleta o no funcional. |
| **4. Explicación del algoritmo que resuelve rompecabezas (10%)** | Explica claramente entradas, salidas, lógica del algoritmo y uso de la base de datos. | Explica la lógica general del algoritmo, con algunos detalles omitidos. | La explicación es básica y deja partes importantes poco claras. | No se comprende cómo funciona el algoritmo. |
| **5. Solución de rompecabezas sin piezas faltantes (20%)** | El algoritmo arma correctamente el rompecabezas completo desde una pieza inicial. | El algoritmo resuelve la mayor parte del rompecabezas, con errores menores. | El algoritmo resuelve parcialmente el rompecabezas. | El algoritmo no resuelve el rompecabezas o requiere intervención manual significativa. |
| **6. Solución de rompecabezas con piezas faltantes (20%)** | Identifica piezas faltantes y arma correctamente la parte posible del rompecabezas. | Maneja piezas faltantes con errores menores en la solución parcial. | Detecta algunas piezas faltantes, pero la solución parcial es limitada. | No maneja correctamente piezas faltantes. |
| **7. Calidad de la presentación (10%)** | Presentación clara, ordenada, estructurada, entretenida y fácil de seguir. | Presentación comprensible, aunque con menor dinamismo o fluidez. | Presentación monótona o desorganizada; transmite el contenido con dificultad. | Presentación confusa, desordenada o incompleta; genera confusión o desinterés. |

