-- auto-generated definition
create table asset_dns_records
(
    id          bigint auto_increment
        primary key,
    domain      varchar(255)                                          not null comment '域名不能是唯一，因为有多个解析',
    priority    varchar(10)                                           null,
    weight      varchar(10)                                           null,
    port        varchar(50)                                           null,
    target      varchar(255)                                          null,
    recordType  enum ('A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SRV') not null,
    recordValue varchar(255) default 'N/A'                            null,
    createTime  datetime(6)  default CURRENT_TIMESTAMP(6)             null,
    updateTime  datetime(6)  default CURRENT_TIMESTAMP(6)             null,
    constraint unique_record
        unique (domain, recordType, recordValue)
)
    comment '域名解析表';

create index asset_dns_records__index_createTime
    on asset_dns_records (createTime);

create index asset_dns_records__index_updateTime
    on asset_dns_records (updateTime);

create index asset_dns_records_id_index
    on asset_dns_records (id);

