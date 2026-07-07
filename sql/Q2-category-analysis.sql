with genres_split as (
	select
	app_id,
	positive,
	negative,
	positive::float / (positive + negative)::float as positive_ratio, 
	trim(unnest(string_to_array(genres, ','))) as genre
	from games
	where 1=1 
	and genres is not null
	and positive + negative >= 50
)
select 
genre,
count(*) as games_count,
round(avg(positive_ratio)::numeric, 3) as avg_ratio,
round(percentile_cont(0.5) within group (order by positive_ratio)::numeric, 3) as median_ratio,
round(stddev(positive_ratio)::numeric, 3 ) as std_dev
from genres_split
where 1=1 
group by 1 
having count(*) >= 100
order by 3 desc