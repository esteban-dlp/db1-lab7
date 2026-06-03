# Informe de Indicadores - Lab 7 Visualización de Datos

**Área asignada:** Ventas

Todos los indicadores fueron diseñados para Metabase usando Native Query / SQL sobre PostgreSQL.

## 1. Ventas totales completadas

1. **Nombre del indicador:** Ventas totales completadas
2. **Qué representa en términos de negocio:** Representa el valor total vendido por RetailMax en transacciones efectivamente completadas.
3. **Por qué es importante para el área de Ventas:** Permite al área de Ventas medir el tamaño real del negocio y evaluar si las acciones comerciales están generando ingresos.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Indicador numérico. Es la visualización más adecuada porque resume un KPI global en una sola cifra ejecutiva.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas_totales
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado';
```

## 2. Cantidad de pedidos completados

1. **Nombre del indicador:** Cantidad de pedidos completados
2. **Qué representa en términos de negocio:** Mide el volumen de transacciones cerradas exitosamente.
3. **Por qué es importante para el área de Ventas:** Ayuda a Ventas a separar crecimiento por cantidad de operaciones frente a crecimiento por monto promedio.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Indicador numérico. Es adecuado porque el valor principal es un conteo global de actividad comercial.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    COUNT(*) AS pedidos_completados
FROM pedido
WHERE estado = 'completado';
```

## 3. Ticket promedio

1. **Nombre del indicador:** Ticket promedio
2. **Qué representa en términos de negocio:** Representa cuánto compra en promedio un cliente cada vez que realiza un pedido completado.
3. **Por qué es importante para el área de Ventas:** Permite evaluar estrategias de venta cruzada, promociones y mezcla de productos desde la perspectiva de ingresos por orden.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Indicador numérico. Es ideal porque resume la intensidad económica de cada pedido en una cifra comparable.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
WITH total_por_pedido AS (
    SELECT
        p.id_pedido,
        SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)) AS total_pedido
    FROM pedido p
    JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
    WHERE p.estado = 'completado'
    GROUP BY p.id_pedido
)
SELECT
    ROUND(AVG(total_pedido), 2) AS ticket_promedio
FROM total_por_pedido;
```

## 4. Ventas mensuales

1. **Nombre del indicador:** Ventas mensuales
2. **Qué representa en términos de negocio:** Muestra la evolución mensual de las ventas completadas de RetailMax.
3. **Por qué es importante para el área de Ventas:** Ventas puede detectar estacionalidad, meses fuertes, caídas y tendencias que requieran acciones comerciales.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Línea. Es la mejor opción porque el indicador describe una tendencia en el tiempo.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    DATE_TRUNC('month', p.fecha)::date AS mes,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY mes
ORDER BY mes;
```

## 5. Ventas por región

1. **Nombre del indicador:** Ventas por región
2. **Qué representa en términos de negocio:** Compara cuánto aporta cada región al total de ventas.
3. **Por qué es importante para el área de Ventas:** Facilita priorizar esfuerzos comerciales, abastecimiento y metas por zona geográfica.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Barras. Es adecuada para comparar categorías regionales de forma clara.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    t.region,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN tienda t ON t.id_tienda = p.id_tienda
WHERE p.estado = 'completado'
GROUP BY t.region
ORDER BY ventas DESC;
```

## 6. Ventas por tienda

1. **Nombre del indicador:** Ventas por tienda
2. **Qué representa en términos de negocio:** Ranking de tiendas según ingresos generados.
3. **Por qué es importante para el área de Ventas:** Ayuda a identificar tiendas líderes, rezagadas y oportunidades de mejora comercial por ubicación.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Barras horizontales. Es adecuada para comparar varias tiendas con nombres largos.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    t.nombre AS tienda,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN tienda t ON t.id_tienda = p.id_tienda
WHERE p.estado = 'completado'
GROUP BY t.nombre
ORDER BY ventas DESC;
```

## 7. Top 10 productos por ingresos

1. **Nombre del indicador:** Top 10 productos por ingresos
2. **Qué representa en términos de negocio:** Identifica los productos que más contribuyen a los ingresos.
3. **Por qué es importante para el área de Ventas:** Ventas puede proteger disponibilidad, promociones y metas sobre los productos de mayor impacto económico.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Barras horizontales. Es la forma más legible para comparar productos y ordenar un top 10.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    pr.nombre AS producto,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ingresos
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN producto pr ON pr.id_producto = dp.id_producto
WHERE p.estado = 'completado'
GROUP BY pr.nombre
ORDER BY ingresos DESC
LIMIT 10;
```

## 8. Top 10 productos por unidades vendidas

1. **Nombre del indicador:** Top 10 productos por unidades vendidas
2. **Qué representa en términos de negocio:** Mide la demanda física de productos independientemente del precio.
3. **Por qué es importante para el área de Ventas:** Ayuda a Ventas a distinguir productos populares de productos caros y a coordinar disponibilidad con operaciones.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Barras horizontales. Es adecuada para ordenar productos por volumen vendido.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    pr.nombre AS producto,
    SUM(dp.cantidad) AS unidades_vendidas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN producto pr ON pr.id_producto = dp.id_producto
WHERE p.estado = 'completado'
GROUP BY pr.nombre
ORDER BY unidades_vendidas DESC
LIMIT 10;
```

## 9. Ventas por categoría

1. **Nombre del indicador:** Ventas por categoría
2. **Qué representa en términos de negocio:** Muestra qué categorías concentran mayor valor de ventas.
3. **Por qué es importante para el área de Ventas:** Permite orientar campañas, metas y decisiones de surtido hacia las líneas de producto con más potencial comercial.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Barras. Es adecuada para comparar varias categorías de negocio.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    c.nombre AS categoria,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN producto pr ON pr.id_producto = dp.id_producto
JOIN categoria c ON c.id_categoria = pr.id_categoria
WHERE p.estado = 'completado'
GROUP BY c.nombre
ORDER BY ventas DESC;
```

## 10. Ventas por canal

1. **Nombre del indicador:** Ventas por canal
2. **Qué representa en términos de negocio:** Compara el aporte comercial de los canales de venta.
3. **Por qué es importante para el área de Ventas:** Ventas puede evaluar el peso del comercio digital frente a tiendas físicas y ajustar acciones por canal.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Pastel. Es adecuada porque solo compara dos proporciones del total.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    p.canal,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY p.canal
ORDER BY ventas DESC;
```

## 11. Ventas por segmento de cliente

1. **Nombre del indicador:** Ventas por segmento de cliente
2. **Qué representa en términos de negocio:** Mide cuánto aportan los clientes VIP, regulares y nuevos.
3. **Por qué es importante para el área de Ventas:** Ayuda a Ventas a priorizar retención, adquisición y estrategias diferenciadas por segmento.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Barras. Es adecuada para comparar el aporte de cada segmento.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    c.segmento,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN cliente c ON c.id_cliente = p.id_cliente
WHERE p.estado = 'completado'
GROUP BY c.segmento
ORDER BY ventas DESC;
```

## 12. Métodos de pago más usados

1. **Nombre del indicador:** Métodos de pago más usados
2. **Qué representa en términos de negocio:** Muestra las preferencias de pago de los clientes que completan compras.
3. **Por qué es importante para el área de Ventas:** Ventas puede entender fricción de cobro y coordinar promociones o mejoras de experiencia por método de pago.
4. **Qué tipo de visualización se usó y por qué es la más adecuada:** Pastel. Es adecuada porque compara la participación relativa de tres métodos de pago.
5. **Consulta SQL completa usada para generarlo en Metabase:**

```sql
SELECT
    pg.metodo,
    COUNT(*) AS cantidad_pagos
FROM pago pg
JOIN pedido p ON p.id_pedido = pg.id_pedido
WHERE p.estado = 'completado'
GROUP BY pg.metodo
ORDER BY cantidad_pagos DESC;
```
