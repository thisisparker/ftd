-- Schema for FOIA The Dead requests

create table requests (
    id                  integer primary key autoincrement not null,
    name                text,
    obit_headline       text,   
    obit_url            text,
    requested_at        datetime,
    acknowledged_on     datetime,
    request_blogged_at  datetime,
    request_blog_url    text,
    response_due_on     datetime,
    response            text,
    response_at         datetime,
    response_blogged_at datetime,
    response_blog_url   text
);
