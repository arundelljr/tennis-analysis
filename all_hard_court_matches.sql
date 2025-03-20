with all_matches as (
	select cast(cast(tourney_date as varchar(4)) as int) as match_year, surface, tourney_level, 
		winner_name, winner_ht, w_ace, w_svpt, 
		loser_name, loser_ht, l_ace, l_svpt 
	from atp_matches_singles
	),

surfaces as (
	select distinct surface from all_matches
	),	

winners as (
	select match_year, surface, tourney_level, winner_name as "name", winner_ht as "ht", w_ace as "aces", w_svpt as "svpts" 
	from all_matches
	),

losers as (
	select match_year, surface, tourney_level, loser_name as "name", loser_ht as "ht", l_ace as "aces", l_svpt as "svpts" 
	from all_matches
	),

joined_matches as (
	select * from winners
	union all
	select * from losers
	),
	
hard_matches as (
	select * from joined_matches
	where surface = 'Hard'
	),

grass_matches as (
	select * from joined_matches
	where surface = 'Grass'
	),

clay_matches as (
	select * from joined_matches
	where surface = 'Clay'
	),

carpet_matches as (
	select * from joined_matches
	where surface = 'Carpet'
	)

select name, round(cast(avg(ht) as numeric), 0) as ht, sum(aces) as aces, sum(svpts) as svpts, round(cast((sum(aces) / sum(svpts)) as numeric) * 100, 1) as ace_percentage, count(*) as total_matches 
from hard_matches
where aces is not null and ht is not null and svpts != 0
group by name
order by ace_percentage desc;