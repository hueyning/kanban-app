drop table if exists do;
create table do (
  id integer primary key,
  title text not null,
  'text' text not null,
  status text not null, 
  user_id integer not null, 
  foreign key (user_id) references users(id) 
);

drop table if exists users;
create table users (
	id integer primary key,
	username text not null,
	password text not null,
	email text not null
);