-- auto-generated definition
create table asset_dns_white
(
    id         bigint auto_increment
        primary key,
    owner      varchar(255)                             null,
    email      varchar(255)                             null,
    domain     varchar(255)                             not null,
    isWhite    varchar(20) default '0'                  null,
    note       varchar(255)                             null,
    createTime datetime(6) default CURRENT_TIMESTAMP(6) null,
    updateTime datetime(6) default CURRENT_TIMESTAMP(6) null,
    constraint domainName
        unique (domain)
)
    comment '域名加白表';

create index asset_dns_white__index_createTime
    on asset_dns_white (createTime);

create index asset_dns_white__index_id
    on asset_dns_white (id);

create index asset_dns_white__index_updateTime
    on asset_dns_white (updateTime);

