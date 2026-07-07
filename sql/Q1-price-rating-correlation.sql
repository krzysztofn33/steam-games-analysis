with game_statistics as (
	select 
	case when price = 0 then 'Free'
	when price < 5 then '$0-5'
	when price < 15 then '$5-15'
	when price < 30 then '$15-30'
	when price < 60 then '$30-60'
	else '$60+'
	end as price_bucket,
	positive::float / (positive+negative)::float as positive_ratio
	from games
	where (positive + negative) >= 50 --at least 50 ratings
)
select 
    price_bucket,
    count(*) as num_of_games,
    round(avg(positive_ratio)::numeric, 3) as avg_ratio,
    round(percentile_cont(0.5) within group (order by positive_ratio)::numeric, 3) as median_ratio,
    round(stddev(positive_ratio)::numeric, 3) as std_dev,
    round(min(positive_ratio)::numeric, 3) as min_ratio,
    round(max(positive_ratio)::numeric, 3) as max_ratio
from game_statistics
group by 1
order by 
    case price_bucket
        when 'Free'   then 1
        when '$0-5'   then 2
        when '$5-15'  then 3
        when '$15-30' then 4
        when '$30-60' then 5
        when '$60+'   then 6
end