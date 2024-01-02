WITH potatoes AS (
    SELECT *
    FROM {{ ref('raw_potatoes')}}
),
final AS (
    SELECT
        id AS potato_id,
        name,
        color,
        taste,
        rarity,
        score,
        price
    from potatoes
)

SELECT *
FROM final
