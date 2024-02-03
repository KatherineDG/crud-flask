drop table if exists cliente;

create table cliente(
    dni int primary key not null,
    nombre varchar(200) not null,
    apellido varchar(200) not null,
    mail varchar(200) not null,
    creado timestamp default current_date,
    foto text
)