with monthly_stats as (
    select
        extract(month from release_date)::int as release_month,
        to_char(release_date, 'month') as month_name,
        count(*) as games_released,
        avg(positive::float / (positive + negative)) as avg_ratio,
        avg(positive + negative) as avg_reviews
    from games
    where release_date >= '2010-01-01'
      and (positive + negative) >= 50
	
    group by extract(month from release_date), to_char(release_date, 'month')
)
select
    release_month,
    trim(month_name) as month,
    games_released,
    round(avg_ratio::numeric, 3) as avg_ratio,
    round(avg_reviews::numeric, 0) as avg_reviews,
    rank() over (order by avg_ratio desc) as rank_by_rating,
    rank() over (order by avg_reviews desc) as rank_by_popularity
from monthly_stats
order by release_month