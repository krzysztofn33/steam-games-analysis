with ranked_games as (
    select
        name,
        price,
        positive,
        negative,
        positive + negative as total_reviews,
        positive::float / (positive + negative) as positive_ratio,
        average_playtime,
        ntile(100) over (order by (positive + negative) desc) as percentile
    from games
    where (positive + negative) >= 50
)
select
    case when percentile = 1 then 'top 1%' else 'rest (99%)' end as segment,
    count(*) as games_count,
    round(avg(price)::numeric, 2) as avg_price,
    round(avg(positive_ratio)::numeric, 3) as avg_ratio,
    round(avg(total_reviews)::numeric, 0) as avg_reviews,
    round(percentile_cont(0.5) within group (order by total_reviews)::numeric, 0) as median_reviews,
    round(avg(average_playtime)::numeric, 0) as avg_playtime_min,
    round((count(*) filter (where price = 0)::float / count(*) * 100)::numeric, 1) as pct_free
from ranked_games
group by case when percentile = 1 then 'top 1%' else 'rest (99%)' end