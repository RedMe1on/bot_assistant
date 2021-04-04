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
    ('Если вы не готовы рискнуть обычным, вам придется довольствоваться заурядным', 'Джим Рон'),
    ('Жизнь пронесется, как одно мгновенье,\n'
     'Ее цени, в ней черпай наслажденье.\n'
     'Как проведешь ее — так и пройдет,\n'
     'Не забывай: она — твое творенье.', 'Омар Хайям'),
    ('Мы источник веселья — и скорби рудник.\n
     'Мы вместилище скверны — и чистый родник.\n
     'Человек, словно в зеркале мир — многолик.\n
     'Он ничтожен — и он же безмерно велик!', 'Омар Хайям'),
    ('В одно окно смотрели двое.\n'
     'Один увидел дождь и грязь.\n'
     'Другой - листвы зеленой вязь,\n'
     'весну и небо голубое.\n'
     'В одно окно смотрели двое.', 'Омар Хайям');



insert into compliments(text) values ('Комплимент');