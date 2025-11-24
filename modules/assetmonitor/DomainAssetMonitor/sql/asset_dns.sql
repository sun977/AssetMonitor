-- auto-generated definition
create table asset_dns
(
    id         bigint auto_increment comment 'ID',
    createTime datetime(6) default CURRENT_TIMESTAMP(6) null comment '创建时间',
    updateTime datetime(6) default CURRENT_TIMESTAMP(6) null on update CURRENT_TIMESTAMP(6) comment '更新时间',
    domain     varchar(255)                             not null comment '域名',
    domainType varchar(255)                             null comment '域名类型',
    dnsServer  varchar(255)                             null comment 'dns应答服务器',
    answerIp   varchar(255)                             null comment '域名解析IP',
    isCdn      int         default 0                    null comment '是否CDN',
    isUse      int         default 0                    null comment '域名是否在使用',
    isWhite    int         default 0                    null comment '域名是否加白',
    note       varchar(255)                             null,
    primary key (id, domain),
    constraint asset_dns_index_domain
        unique (domain)
)
    comment '域名有效性监控表';

create index asset_dns__index_createTime
    on asset_dns (createTime);

create index asset_dns__index_updateTime
    on asset_dns (updateTime);

create index asset_dns_id_index
    on asset_dns (id);

