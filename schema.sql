-- Schema for FOIA The Dead requests

create table requests (
    id                  integer primary key autoincrement not null,
    name                text,
    obit_headline       text,   
    obit_url            text,
    requested_at        datetime,
    documentcloud_id    text,
    slug                text,
    short_description   text,
    long_description    text
);
