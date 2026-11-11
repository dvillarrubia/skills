# Momentos de clase · Barsel · molienda para cafetera italiana

Hallazgos reales del expediente que merece la pena proyectar y discutir. Cada uno con el fichero donde se ve.

## 1. La marca es invisible para la IA, incluso cuando se pide comprar
En las 3 preguntas a asistentes, Barsel sale **citada 0, mencionada 0, ausente 3/3**. En la tercera
(«¿qué café de especialidad me recomiendas comprar online en España?») el asistente recomienda a competidores
(El Criollo, MyWay, Incapto, Nomad) pero **no a Barsel**.
→ `04-asistentes.csv` (columna marca_propia) y `04-fuentes.csv` (22 dominios citados, 0 de cafebarsel).
Debate: tener buen contenido no basta; hay que estar presente donde el asistente busca (fan-out en `04-fan-out.csv`).

## 2. Barsel tampoco aparece en Google ni en su respuesta de IA
En los 9 grupos de consultas, la nota es siempre «crear: ninguna URL propia en los primeros resultados».
La respuesta de IA de Google aparece en 2 de 10 consultas y enlaza a cafebarsel.com en **0 ocasiones**.
→ final de `_log_03.txt` y `03-grupos.csv`.
Debate: la marca sí tiene páginas del tema (P1, P2, P3) pero no rankean. Visibilidad ≠ existir.

## 3. Las URLs de la estructura antigua devuelven 404 (no redirigen)
Las tres URLs antiguas de `caso.toml` dan **HTTP 404**, no un 301 a la nueva estructura.
→ `_log_05.txt` (sección «URLs de la estructura anterior»).
Debate: cada 404 es autoridad y enlaces que se tiran a la basura en una migración mal rematada.

## 4. La verificación de citas funcionando en directo
En cobertura, **2 notas se anulan** porque el fragmento citado no está literalmente en la página («sin evidencia»).
En evidencias, al principio se descartan afirmaciones cuyo fragmento no aparece en la página propia.
→ `06-cobertura.csv` (celdas «SE») y el log `_log_06.txt` («2 notas anuladas»).
Debate: así se corta de raíz que el modelo «atribuya» a una página algo que no dice.

## 5. Fuentes que se contradicen: ¿gruesa o media?
La página de un competidor (cafesbou, P5) afirma que la molienda **gruesa** es «ideal» para la cafetera italiana,
mientras bonka (P4) y cafeirreverentes (P7) dicen **media/media-fina**. El borrador descarta a propósito la de P5.
→ `06-cobertura.csv` (tema «Qué molienda usar», fila P5) y `09-instrucciones.md` (apartado 7, PENDIENTE).
Debate: que una afirmación esté publicada no la hace cierta; aquí hay un conflicto real entre marcas.

## 6. El crítico es código: el borrador converge 3 → 1 → 0 fallos
La v0 tenía 3 fallos; la v1 bajó a 1 pero **se pasó de corto** (0 % de frases largas, cuando la marca escribe
entre 2,34 y 7,86 %); la v2 ajustó y quedó en 0. La nota final la calcula Python: **83,8/100, APTO**.
→ `_log_10.txt` (versiones) y `12-revision.md`.
Debate: «optimizado para la voz de la marca» es un rango medible, no «más corto siempre es mejor».
