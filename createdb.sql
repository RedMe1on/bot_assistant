create table tasks(
    id integer primary key,
    description text,
    date_ text
);

create table quotes_of_the_day(
    id integer primary key,
    text text,
    author varchar(255)
);

create table compliments(
    id integer primary key,
    text text
);

insert into tasks (id, description, date_)
values
    (1, "Сделать что-то", date('now')),
    (2, "Сделать что-то 2", date('now'));

insert into quotes_of_the_day(text, author) values ('Цитата', 'Автор');

insert into compliments(text) values ('Комплимент');