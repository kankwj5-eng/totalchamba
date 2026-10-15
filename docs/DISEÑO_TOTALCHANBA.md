# TotalChanba 4.0 — reglas de diseño

- Tarjetas tipo expediente, adaptables, con imagen ilustrativa del oficio (no de la empresa).
- Avatares de animalitos se generan localmente de forma determinista según el nombre anunciado; no son logos, sellos, testimonios ni verificación de identidad.
- Cuatro hechos destacados: lugar, modalidad, contrato y salario; lo no informado siempre aparece como tal.
- Ficha extendida agrupa empresa, fecha, descripción suministrada, fuente, ubicación según precisión declarada, estrellas explicables y enlace a la publicación original.
- Sin reseñas inventadas, indicadores falsos de confiabilidad, salarios estimados disfrazados de oficiales ni números de empleos fabricados.
- Fotografía real de empresas sólo con permisos, créditos y trazabilidad; por defecto recursos gráficos locales por oficio, sin llamadas a terceros.
- Botones guardar, comparar y compartir; atajos de teclado y lectura clara.

La interfaz cambia de marca a TotalChanba. El repositorio utiliza la escritura `totalchamba` y no se altera su URL.


## Evolución v5

- 12 fotografías generadas con IA para sectores/oficios, almacenadas en WebP locales (<70 KB por imagen). Se muestra aviso de ilustración junto a cada fotografía; nunca implican un empleador o instalación real.
- Las fotografías se seleccionan por palabras clave del puesto, no por el nombre de la empresa; el avatar de animalito no representa una identidad corporativa.
- Los datos opcionales `requirements`, `benefits`, `experience`, `education` solo aparecen cuando la fuente los proporciona. No se infiere la remuneración ni se añaden certificaciones.
- Un aviso visible aparece cuando el índice es de muestra o su fecha de generación es antigua; mantenerlo hasta que el agente recolecte datos reales comprobados.
