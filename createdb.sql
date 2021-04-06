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
    (1, "Сделать что-то", '07/04/2021'),
    (2, "Сделать что-то 2", '07/04/2021');

insert into quotes(text, author) values
    ('Если вы не готовы рискнуть обычным, вам придется довольствоваться заурядным', 'Джим Рон'),
    ('Жизнь пронесется, как одно мгновенье,\nЕе цени, в ней черпай наслажденье.\nКак проведешь ее — так и пройдет,\nНе забывай: она — твое творенье.', 'Омар Хайям'),
    ('Мы источник веселья — и скорби рудник.\nМы вместилище скверны — и чистый родник.\nЧеловек, словно в зеркале мир — многолик.\nОн ничтожен — и он же безмерно велик!', 'Омар Хайям'),
    ('В одно окно смотрели двое.\nОдин увидел дождь и грязь.\nДругой - листвы зеленой вязь,\nвесну и небо голубое.\nВ одно окно смотрели двое.', 'Омар Хайям');



insert into compliments(text) values ('Комплимент');