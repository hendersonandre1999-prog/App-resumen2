# PROMPT – APLICACIÓN WEB SHIIFT CON BÚSQUEDAS Y FILTROS DINÁMICOS

Actúa como diseñador UX/UI y desarrollador experto en aplicaciones web empresariales y dashboards interactivos.

Desarrolla una aplicación web moderna para consultar y analizar la información del archivo Excel **Control Oficial SHIIFT 2app.py.xlsb**.

## 1. ORIGEN DE LOS DATOS

Utilizar exclusivamente las hojas individuales del Excel que contienen información de requerimientos.

Excluir completamente:
- RESUMEN.
- Resumen Macro.

No utilizar estas hojas para alimentar indicadores, tablas, gráficas ni filtros.

Evitar duplicar registros y conservar todos los campos originales disponibles.

## 2. DISEÑO DE LA APLICACIÓN

Crear una interfaz moderna y profesional tomando como referencia la imagen proporcionada.

Incluir:
- Menú lateral.
- Dashboard principal.
- Tarjetas de indicadores.
- Gráficas interactivas.
- Buscadores y filtros.
- Tablas detalladas.

## 3. BUSCADOR PRINCIPAL Y FILTROS DINÁMICOS

Esta es la funcionalidad más importante de la aplicación.

Necesito que cada filtro funcione como un buscador independiente y que, al seleccionar una opción, la aplicación muestre exclusivamente la información relacionada con esa selección.

### Filtro 1. Búsqueda por módulo

Permitir seleccionar un módulo de una lista desplegable.

Al seleccionar un módulo, mostrar automáticamente:

- Nombre del módulo.
- Total de requerimientos.
- Requerimientos por estado.
- Porcentaje de avance.
- Responsables asociados.
- Sprints relacionados.
- Fábricas de desarrollo asociadas.
- Gráficas correspondientes al módulo.
- Tabla con todos los requerimientos de ese módulo.

### Filtro 2. Búsqueda por responsable

Al seleccionar un responsable, mostrar:

- Nombre del responsable.
- Total de requerimientos asignados.
- Módulos en los que participa.
- Sprints asignados.
- Estados de sus requerimientos.
- Porcentaje de avance.
- Tabla con todos los requerimientos que tiene asignados.

### Filtro 3. Búsqueda por Sprint

Al seleccionar un Sprint, mostrar:

- Número o nombre del Sprint.
- Total de requerimientos.
- Módulos relacionados.
- Responsables asignados.
- Distribución por estado.
- Porcentaje de avance.
- Tabla con todos los requerimientos del Sprint seleccionado.

### Filtro 4. Búsqueda por estado

Al seleccionar un estado, mostrar:

- Nombre del estado.
- Cantidad de requerimientos.
- Porcentaje respecto al total filtrado.
- Módulos relacionados.
- Responsables asociados.
- Sprints relacionados.
- Tabla con todos los requerimientos que tengan ese estado.

### Filtro 5. Búsqueda por fábrica de desarrollo

Al seleccionar una fábrica, mostrar:

- Nombre de la fábrica.
- Total de requerimientos asignados.
- Módulos relacionados.
- Responsables asociados.
- Estados de los requerimientos.
- Porcentaje de avance.
- Tabla con todos los requerimientos correspondientes.

### Filtro 6. Búsqueda por prioridad

Al seleccionar una prioridad, mostrar:

- Total de requerimientos.
- Módulos relacionados.
- Estados.
- Responsables.
- Tabla de requerimientos correspondientes.

### Filtro 7. Búsqueda por tipo

Permitir seleccionar un tipo de requerimiento y mostrar todos los registros asociados, con sus respectivos indicadores y gráficas.

### Filtro 8. Búsqueda por fecha estimada

Permitir consultar requerimientos según su fecha estimada, incluyendo rangos de fechas.

Mostrar los requerimientos que correspondan al período seleccionado.

## 4. COMBINACIÓN DE FILTROS

Los filtros deben funcionar de manera conjunta.

Ejemplo:

Si selecciono:
- Módulo: FI-J59.
- Responsable: Juan Pérez.
- Sprint: Sprint 2.
- Estado: En construcción.

La aplicación debe mostrar únicamente los requerimientos que cumplan simultáneamente con esas cuatro condiciones.

Todos los resultados deben actualizarse automáticamente.

Incluir:
- Botón de aplicar filtros, si es necesario.
- Botón de limpiar filtros.
- Indicadores de los filtros activos.
- Cantidad de registros encontrados.

Los filtros deben ser dependientes entre sí: al seleccionar un módulo, las opciones de responsables, Sprints y estados deben actualizarse para mostrar únicamente las opciones que correspondan a los datos disponibles.

## 5. RESULTADOS DE CADA BÚSQUEDA

Cada vez que el usuario realice una búsqueda, mostrar una pantalla de resultados con tres partes:

**A. Indicadores**
- Total de registros encontrados.
- Completados.
- Pendientes.
- En proceso.
- Porcentaje de avance.

**B. Gráficas**
- Distribución por estado.
- Distribución por módulo, cuando corresponda.
- Distribución por responsable.
- Distribución por Sprint.
- Distribución por fábrica.

Las gráficas deben adaptarse automáticamente a los filtros seleccionados.

**C. Detalle de registros**

Mostrar una tabla con todos los requerimientos que coincidan con la búsqueda.

Incluir los campos disponibles:
- ID WRICEF.
- Nombre del requerimiento.
- Módulo.
- Responsable.
- Sprint.
- Fecha estimada.
- Tiempo.
- Avance de refinamiento.
- Tipo.
- Priorización.
- Estado.
- Recurso IT / PM.
- Observaciones.
- Fábrica de desarrollo.

Permitir abrir cada registro para consultar toda su información.

## 6. DASHBOARD GENERAL

Cuando no exista ningún filtro seleccionado, mostrar la información general de todos los módulos.

Incluir tarjetas con:
- Total de requerimientos.
- Completados.
- Pendientes.
- En proceso.
- Desestimados.
- Porcentaje general de avance.

Agregar gráficas de dona, barras, columnas y barras apiladas para visualizar los datos.

## 7. ACTUALIZACIÓN DEL EXCEL

Incluir un botón para cargar y actualizar el archivo Excel.

Al cargar una nueva versión:
- Leer las hojas individuales.
- Ignorar RESUMEN y Resumen Macro.
- Actualizar los registros.
- Actualizar los filtros.
- Actualizar los indicadores.
- Actualizar las gráficas.
- Mantener la información en una base de datos en la nube.

## 8. RESULTADO ESPERADO

Quiero una aplicación que permita buscar información de forma rápida y sencilla.

La funcionalidad principal debe ser que el usuario pueda seleccionar cualquier módulo, responsable, Sprint, estado, fábrica o prioridad y obtener inmediatamente todos los datos correspondientes.

No quiero filtros decorativos que únicamente cambien el nombre de una selección.

**Cada filtro debe realizar una búsqueda real sobre los registros del Excel y mostrar los resultados correspondientes en indicadores, gráficas y tablas.**

La aplicación debe ser completamente funcional, visualmente atractiva y fácil de utilizar para los gerentes y usuarios de consulta.
