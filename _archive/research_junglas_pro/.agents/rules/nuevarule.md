---
trigger: always_on
glob: "**/*"
description: Obliga a revisar la documentacion del proyecto antes de editar y a actualizarla despues de cada modificacion de archivos.
---

# Regla de documentacion obligatoria

Esta regla aplica a cualquier agente de codificacion que trabaje en este proyecto.

## Antes de modificar archivos
1. Leer `docs/registro-tecnico.md`.
2. Leer `docs/guia-operativa-junglas.md` para entender la arquitectura final vigente.
3. Revisar los documentos de `docs/` que impacten el area tocada.
4. Si el cambio afecta la tier list o contenido derivado de esa investigacion, revisar tambien `docs/deeps_searchs/search_profesionales_tierlist.md`.
5. Antes de escribir codigo, verificar si el cambio reintroduce una segunda linea de trabajo, tooling permanente innecesario, archivos duplicados o formatos viejos que contradigan la arquitectura final compacta.
6. Si el estado del repo ya no coincide con la documentacion, corregir la documentacion como parte de la misma tarea.

## Despues de cada modificacion de archivos
1. Actualizar `docs/registro-tecnico.md` en la misma tarea.
2. Registrar como minimo:
   - motivo del cambio
   - archivos modificados
   - descripcion tecnica
   - impacto visible o funcional
   - deuda o seguimiento pendiente
3. Esto aplica incluso si solo se modifica un unico archivo.
4. No se considera terminada una tarea si el codigo cambio y la documentacion no se actualizo.
5. Antes de cerrar la tarea, hacer una pasada de compactacion:
   - borrar archivos temporales, caches, scripts one-off o tooling que ya no participe de la version final
   - eliminar funciones, archivos y documentos que hayan quedado sin uso real
   - evitar dejar dos fuentes de verdad para la misma funcionalidad
   - mantener la pagina activa autocontenida salvo que el cambio exija explicitamente otra arquitectura
   - mantener `WEBP` como formato final de retratos locales salvo nueva decision documentada
6. Si por necesidad tecnica se crea tooling temporal, debe quedar removido al finalizar o documentado explicitamente como parte activa del proyecto.

## Alcance
- Aplica despues de cualquier alta, baja, renombre o edicion de archivos dentro del proyecto.
- Si se crean nuevos documentos en `docs/`, tambien deben quedar mencionados en `docs/registro-tecnico.md`.
- Tambien aplica como regla de higiene arquitectonica: antes de codear se revisa si el cambio encaja con la arquitectura final, y despues de codear se limpia todo residuo que no deba quedar en el repo.
