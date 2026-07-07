select
case when price = 0 then 'F2P' else 'paid' end as pricing_model,
count(*) as games_count,
round(avg(positive::float / (positive + negative))::numeric, 3 ) as avg_ratio,
round(percentile_cont(0.5) within group (order by positive::float / (positive + negative))::numeric, 3) as median_ratio,
round(avg(positive + negative)::numeric, 0) as avg_reviews,
round(percentile_cont(0.5) within group (order by positive + negative)::numeric, 0) as median_reviews,
round(avg(average_playtime)::numeric, 0) as avg_playtime_min,
round(percentile_cont(0.5) within group (order by average_playtime)::numeric, 0) as median_playtime_min
from games
where 1=1 
and (positive + negative) >= 50
group by 1