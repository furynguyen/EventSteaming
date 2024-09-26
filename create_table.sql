

CREATE EXTENSION pg_partman;

CREATE EXTENSION pg_cron;

create table events
(
	_id timestamp primary key not null default current_timestamp,
	id uuid,
	email text,
	event text,
	time timestamptz,
	address text,
	city text,
	ip text
)
PARTITION BY RANGE(_id);

SELECT create_parent('public.events', '_id', 'native', 
                     'daily', p_start_partition := '2024-09-14');
                    