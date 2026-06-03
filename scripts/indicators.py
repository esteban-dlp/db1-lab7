INDICATORS = [
    {
        "key": "ventas_totales",
        "tab": "Desempeño General de Ventas",
        "name": "Ventas totales completadas",
        "description": "Suma de ingresos brutos descontados de pedidos completados.",
        "business": "Representa el valor total vendido por RetailMax en transacciones efectivamente completadas.",
        "importance": "Permite al área de Ventas medir el tamaño real del negocio y evaluar si las acciones comerciales están generando ingresos.",
        "visualization": "Indicador numérico. Es la visualización más adecuada porque resume un KPI global en una sola cifra ejecutiva.",
        "display": "scalar",
        "sql": """
SELECT
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas_totales
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado';
""".strip(),
    },
    {
        "key": "pedidos_completados",
        "tab": "Desempeño General de Ventas",
        "name": "Cantidad de pedidos completados",
        "description": "Número de pedidos con estado completado.",
        "business": "Mide el volumen de transacciones cerradas exitosamente.",
        "importance": "Ayuda a Ventas a separar crecimiento por cantidad de operaciones frente a crecimiento por monto promedio.",
        "visualization": "Indicador numérico. Es adecuado porque el valor principal es un conteo global de actividad comercial.",
        "display": "scalar",
        "sql": """
SELECT
    COUNT(*) AS pedidos_completados
FROM pedido
WHERE estado = 'completado';
""".strip(),
    },
    {
        "key": "ticket_promedio",
        "tab": "Desempeño General de Ventas",
        "name": "Ticket promedio",
        "description": "Promedio de venta por pedido completado.",
        "business": "Representa cuánto compra en promedio un cliente cada vez que realiza un pedido completado.",
        "importance": "Permite evaluar estrategias de venta cruzada, promociones y mezcla de productos desde la perspectiva de ingresos por orden.",
        "visualization": "Indicador numérico. Es ideal porque resume la intensidad económica de cada pedido en una cifra comparable.",
        "display": "scalar",
        "sql": """
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
""".strip(),
    },
    {
        "key": "ventas_mensuales",
        "tab": "Desempeño General de Ventas",
        "name": "Ventas mensuales",
        "description": "Ingresos completados agrupados por mes.",
        "business": "Muestra la evolución mensual de las ventas completadas de RetailMax.",
        "importance": "Ventas puede detectar estacionalidad, meses fuertes, caídas y tendencias que requieran acciones comerciales.",
        "visualization": "Línea. Es la mejor opción porque el indicador describe una tendencia en el tiempo.",
        "display": "line",
        "sql": """
SELECT
    DATE_TRUNC('month', p.fecha)::date AS mes,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY mes
ORDER BY mes;
""".strip(),
    },
    {
        "key": "ventas_por_region",
        "tab": "Desempeño General de Ventas",
        "name": "Ventas por región",
        "description": "Ingresos completados agrupados por región de tienda.",
        "business": "Compara cuánto aporta cada región al total de ventas.",
        "importance": "Facilita priorizar esfuerzos comerciales, abastecimiento y metas por zona geográfica.",
        "visualization": "Barras. Es adecuada para comparar categorías regionales de forma clara.",
        "display": "bar",
        "sql": """
SELECT
    t.region,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN tienda t ON t.id_tienda = p.id_tienda
WHERE p.estado = 'completado'
GROUP BY t.region
ORDER BY ventas DESC;
""".strip(),
    },
    {
        "key": "ventas_por_tienda",
        "tab": "Desempeño General de Ventas",
        "name": "Ventas por tienda",
        "description": "Ingresos completados agrupados por punto de venta.",
        "business": "Ranking de tiendas según ingresos generados.",
        "importance": "Ayuda a identificar tiendas líderes, rezagadas y oportunidades de mejora comercial por ubicación.",
        "visualization": "Barras horizontales. Es adecuada para comparar varias tiendas con nombres largos.",
        "display": "bar",
        "sql": """
SELECT
    t.nombre AS tienda,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN tienda t ON t.id_tienda = p.id_tienda
WHERE p.estado = 'completado'
GROUP BY t.nombre
ORDER BY ventas DESC;
""".strip(),
    },
    {
        "key": "top_productos_ingresos",
        "tab": "Productos, Clientes y Canales",
        "name": "Top 10 productos por ingresos",
        "description": "Productos con mayor venta completada en quetzales.",
        "business": "Identifica los productos que más contribuyen a los ingresos.",
        "importance": "Ventas puede proteger disponibilidad, promociones y metas sobre los productos de mayor impacto económico.",
        "visualization": "Barras horizontales. Es la forma más legible para comparar productos y ordenar un top 10.",
        "display": "bar",
        "sql": """
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
""".strip(),
    },
    {
        "key": "top_productos_unidades",
        "tab": "Productos, Clientes y Canales",
        "name": "Top 10 productos por unidades vendidas",
        "description": "Productos con mayor cantidad de unidades vendidas en pedidos completados.",
        "business": "Mide la demanda física de productos independientemente del precio.",
        "importance": "Ayuda a Ventas a distinguir productos populares de productos caros y a coordinar disponibilidad con operaciones.",
        "visualization": "Barras horizontales. Es adecuada para ordenar productos por volumen vendido.",
        "display": "bar",
        "sql": """
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
""".strip(),
    },
    {
        "key": "ventas_por_categoria",
        "tab": "Productos, Clientes y Canales",
        "name": "Ventas por categoría",
        "description": "Ingresos completados agrupados por categoría de producto.",
        "business": "Muestra qué categorías concentran mayor valor de ventas.",
        "importance": "Permite orientar campañas, metas y decisiones de surtido hacia las líneas de producto con más potencial comercial.",
        "visualization": "Barras. Es adecuada para comparar varias categorías de negocio.",
        "display": "bar",
        "sql": """
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
""".strip(),
    },
    {
        "key": "ventas_por_canal",
        "tab": "Productos, Clientes y Canales",
        "name": "Ventas por canal",
        "description": "Distribución de ingresos completados entre tienda y online.",
        "business": "Compara el aporte comercial de los canales de venta.",
        "importance": "Ventas puede evaluar el peso del comercio digital frente a tiendas físicas y ajustar acciones por canal.",
        "visualization": "Pastel. Es adecuada porque solo compara dos proporciones del total.",
        "display": "pie",
        "sql": """
SELECT
    p.canal,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
WHERE p.estado = 'completado'
GROUP BY p.canal
ORDER BY ventas DESC;
""".strip(),
    },
    {
        "key": "ventas_por_segmento",
        "tab": "Productos, Clientes y Canales",
        "name": "Ventas por segmento de cliente",
        "description": "Ingresos completados agrupados por segmento de cliente.",
        "business": "Mide cuánto aportan los clientes VIP, regulares y nuevos.",
        "importance": "Ayuda a Ventas a priorizar retención, adquisición y estrategias diferenciadas por segmento.",
        "visualization": "Barras. Es adecuada para comparar el aporte de cada segmento.",
        "display": "bar",
        "sql": """
SELECT
    c.segmento,
    ROUND(SUM(dp.cantidad * dp.precio_unitario * (1 - dp.descuento / 100.0)), 2) AS ventas
FROM pedido p
JOIN detalle_pedido dp ON dp.id_pedido = p.id_pedido
JOIN cliente c ON c.id_cliente = p.id_cliente
WHERE p.estado = 'completado'
GROUP BY c.segmento
ORDER BY ventas DESC;
""".strip(),
    },
    {
        "key": "metodos_pago",
        "tab": "Productos, Clientes y Canales",
        "name": "Métodos de pago más usados",
        "description": "Conteo de pagos por método en pedidos completados.",
        "business": "Muestra las preferencias de pago de los clientes que completan compras.",
        "importance": "Ventas puede entender fricción de cobro y coordinar promociones o mejoras de experiencia por método de pago.",
        "visualization": "Pastel. Es adecuada porque compara la participación relativa de tres métodos de pago.",
        "display": "pie",
        "sql": """
SELECT
    pg.metodo,
    COUNT(*) AS cantidad_pagos
FROM pago pg
JOIN pedido p ON p.id_pedido = pg.id_pedido
WHERE p.estado = 'completado'
GROUP BY pg.metodo
ORDER BY cantidad_pagos DESC;
""".strip(),
    },
]

TABS = [
    "Desempeño General de Ventas",
    "Productos, Clientes y Canales",
]
