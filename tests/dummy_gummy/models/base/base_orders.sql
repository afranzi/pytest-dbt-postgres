WITH orders AS (
    SELECT *
    FROM {{ source('external', 'orders') }}
),

final AS (
    SELECT
        id as order_id,
        customer_id,
        potato_id,
        quantity
    FROM orders
)

SELECT * 
FROM final