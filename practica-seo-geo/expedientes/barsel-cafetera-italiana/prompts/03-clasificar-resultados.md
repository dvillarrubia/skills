# Prompt: 03-clasificar-resultados

## Sistema

Clasificas resultados de búsqueda a partir de su título, descripción y URL. Es una inferencia: no has leído las páginas. Devuelve solo JSON.

## Usuario

Consulta: molienda para cafetera italiana

Resultados:
1. Molienda del café: un tipo para cada cafetera | https://www.bonka.es/amor-por-el-cafe/molienda-cafe | Por eso el más indicado para una cafetera italiana es el café de molienda media, como el café Bonka Molido Extrafuerte especial para cafeteras italianas. La ...
2. Qué tipo de molienda es mejor para una cafetera italiana | https://shop.cafesbou.com/blogs/news/que-tipo-de-molienda-es-mejor-para-una-cafetera-italiana?srsltid=AYCX9vIZazMO5DTTWgu0yGMa23bMB8CnsRLIQVGDQJv2E2Ft8Pa_ZIRT | Utiliza una molienda media-fina, algo más gruesa que la de espresso. Así evitas una extracción excesiva y consigues un café intenso pero equilibrado, sin notas ...
3. Grado de molienda para la italiana | https://forocafe.es/foro/viewtopic.php?t=2853 | En mi caso, para la italiana, el café lo muelo con un molinillo manual para no cambiar la configuración del eléctrico, porque además necesita ...
4. Tipos de molienda de café: guía para tu cafetera | https://cafeirreverentes.com/blog/tipos-de-molienda-de-cafe/ | La mejor molienda para cafetera italiana suele ser media o media-fina. Debe parecerse a arena fina, pero no llegar a ser tan fina como la ...
5. Cómo elegir la molienda del café según tu cafetera | https://dfrnt.coffee/blogs/info/como-elegir-la-molienda-del-cafe-segun-tu-cafetera?srsltid=AYCX9vJ7eGT7ra9hGRtsBHEhMTFzDa-ugE_AHUd2pZNZuhPeFXm67E7Z | ¿Qué molienda usar para cafetera italiana? La cafetera moka necesita molienda media-fina, similar a azúcar. ¿Qué molienda usar para V60? La V60 necesita ...
6. Koh – Guía Para Elegir La Molienda Adecuada | https://koffeeonhome.com/guia-molienda-cafe/?srsltid=AYCX9vKMIBkxz5SQqGSI94vvH02UiDW2NwVtcvL9mG3GDbeYQDlbXbzP | Molido Italiana (Moka). Ideal para: cafeteras italianas o moka. Textura: intermedia entre espresso y filtro. Resultado: café intenso, con cuerpo y aroma ...
7. ¿Qué grado de molienda usar y cómo influye al preparar ... | https://www.cafescandelas.com/es/blog/grado-molienda-influye-cafe | El punto de molienda debe adaptarse al tipo de cafetera; el grosor debe ser mayor cuanto más dure el tiempo de extracción de café.

Lista JSON, un objeto por resultado: {"posicion": n, "tipo_pagina": "tienda|blog de marca|medio|foro|vídeo|comparador|otro", "tarea": "qué quiere resolver quien llega", "formato": "guía|lista|ficha|respuesta breve|otro"}
