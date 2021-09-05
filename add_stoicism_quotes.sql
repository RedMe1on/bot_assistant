create table if not exists stoicism_quote(
    id integer primary key,
    text text,
    author varchar(255)
);

insert into stoicism_quote(text, author) values
    ('80% успеха — это появиться в нужном месте в нужное время','Вуди Аллен'),





UPDATE compliments SET text = 'Ты не боишься быть собой. Как же это круто!' WHERE text = 'Ты невероятна, когда не боишься быть собой';