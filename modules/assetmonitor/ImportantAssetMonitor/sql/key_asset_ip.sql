-- auto-generated definition
create table key_asset_ip
(
    id         bigint auto_increment comment '资产ID'
        primary key,
    ip         varchar(255)                             not null comment '资产IP',
    project    varchar(255)                             null comment '资产所属项目',
    owner      varchar(255)                             null comment '资产所属人',
    status     varchar(20) default '1'                  null comment '资产监控状态1启用0关闭',
    note       varchar(255)                             null comment '备注',
    createTime datetime(6) default CURRENT_TIMESTAMP(6) null,
    updateTime datetime(6) default CURRENT_TIMESTAMP(6) null on update CURRENT_TIMESTAMP(6),
    constraint key_asset_ip_ip_uindex
        unique (ip)
)
    comment '重点资产监控表';

create index key_asset_ip__index_createTime
    on key_asset_ip (createTime);

create index key_asset_ip__index_updateTime
    on key_asset_ip (updateTime);

