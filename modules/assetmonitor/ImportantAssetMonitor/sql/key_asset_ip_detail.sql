-- auto-generated definition
create table key_asset_ip_detail
(
    id                        bigint auto_increment,
    ipassetsIp                varchar(255)                             not null comment 'SEC资产ipassets_ip字段',
    ipassetsProjectName       varchar(255)                             null comment 'sec资产ipassets_project_name字段',
    ipassetsBusinessSystem    varchar(255)                             null comment 'SEC资产ipassets_businessSystem字段',
    ipassetsOpsOperationsName varchar(255)                             null comment 'SEC资产ipassets_ops_operations_name字段',
    ipassetsStatus            varchar(255)                             null comment 'SEC平台ipassets_status字段',
    jowtoOnlineStatus         varchar(255)                             null comment 'SEC资产jowto_onlineStatus',
    ipassetsHasVul            varchar(255)                             null comment 'SEC资产ipassets_has_vul',
    ipassetsLogStatus         varchar(255)                             null comment 'SEC资产ipassets_log_status',
    note                      varchar(500)                             null comment '备注',
    createTime                datetime(6) default CURRENT_TIMESTAMP(6) null,
    updateTime                datetime(6) default CURRENT_TIMESTAMP(6) null,
    primary key (id, ipassetsIp),
    constraint key_asset_ip_detail_id_uindex
        unique (id),
    constraint key_asset_ip_detail_ipassetsIp_uindex
        unique (ipassetsIp)
)
    comment '重点资产监控结果表';

create index key_asset_ip_detail__index_createTime
    on key_asset_ip_detail (createTime);

create index key_asset_ip_detail__index_updateTime
    on key_asset_ip_detail (updateTime);

