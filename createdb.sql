create table tasks(
    id integer primary key,
    description text,
    date_ text
);

create table quotes(
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

insert into quotes(text, author) values
    ('Если вы не готовы рискнуть обычным, вам придется довольствоваться заурядным', 'Джим Рон');




insert into compliments(text) values ('Комплимент');