WITH customers AS (
    SELECT *
    FROM {{ source('external', 'customers') }}
),

final AS (
    SELECT 
        id as customer_id,
        name,
        created_at
    FROM customers
)

SELECT *
FROM final