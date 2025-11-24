-- auto-generated definition
create table asset_dns_origin
(
    id         bigint auto_increment
        primary key,
    domain     varchar(255)                             null,
    owner      varchar(255)                             null,
    note       varchar(255)                             null,
    createTime datetime(6) default CURRENT_TIMESTAMP(6) null,
    updateTime datetime(6) default CURRENT_TIMESTAMP(6) null,
    constraint asset_dns_origin_domain_uindex
        unique (domain)
)
    comment '原始域名表';

create index asset_dns_origin__index_createTime
    on asset_dns_origin (createTime);

create index asset_dns_origin__index_updateTime
    on asset_dns_origin (updateTime);

create index asset_dns_origin_id_index
    on asset_dns_origin (id);

