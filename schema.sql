drop table if exists applications;
create table applications (
    id integer primary key autoincrement,
    company string not null,
    position string,
    date string,
    status string not null,
    contact string,
    email string,
    notes text,
    interview text
);
