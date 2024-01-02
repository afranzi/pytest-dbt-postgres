WITH potatoes AS (
    SELECT *
    FROM {{ ref('base_potatoes') }}
),

orders AS (
    SELECT *
    FROM {{ ref('base_orders') }}
),

customer AS (
    SELECT *
    FROM {{ ref('base_customers') }}
),

potato_sales AS (
    SELECT
        customer.customer_id,
        customer.name AS customer_name,
        potatoes.name AS potato_name,
        COUNT(DISTINCT orders.order_id) AS orders,
        SUM(orders.quantity) AS quantity,
        SUM(orders.quantity * potatoes.price) AS price
    FROM customer
    JOIN orders USING(customer_id)
    JOIN potatoes USING(potato_id)
    GROUP BY 1,2,3
    ORDER BY 1,2,3
),

final AS (
    SELECT
        customer_name,
        potato_name,
        orders,
        quantity,
        price,
        SUM(price) OVER (PARTITION BY customer_id) AS total_price
    FROM potato_sales
)

SELECT *
FROM final
