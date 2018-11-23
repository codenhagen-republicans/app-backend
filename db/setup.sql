create user green_app with login password 'green_app';

GRANT pg_read_server_files TO green_app;

drop database if exists green_api;

create database green_app
    encoding 'UTF8'
    owner green_app;
grant all on database green_app to green_app;

\connect green_app green_app;

create table test (
    id              bigserial    primary key,
    other_thing     text
);

