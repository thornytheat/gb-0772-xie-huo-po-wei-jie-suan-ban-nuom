class DocketError(ValueError):
    def __init__(self, code, message, status=422):
        super().__init__(message)
        self.code, self.status = code, status


LABEL = {
    'WIDTH':'表单列数错误','BLANK':'空白记录','TIMESTAMP':'时间戳无效','INTERVAL':'区间倒置',
    'UNKNOWN_BERTH':'泊位不存在','RANGE':'窗外记录','UNSET':'字段缺失','DUPLICATE':'重复记录',
    'ID_CONFLICT':'同编号冲突','PLATE':'车牌格式错误','BAD_STATUS':'预约状态无效',
    'PLATE_OVERLAP':'多个车在同一泊位','BERTH_OVERLAP':'同车同时出现在多个泊位',
    'FREE':'预约首免','BASE':'基础价','UPGRADE':'升级价','CANCELLED':'到达前预约撤销',
    'BOOKED':'预约已关联','WALK_IN':'无生效预约','GAP':'实收差价','MATCH':'实收一致',
    'NO_PAYMENT':'无实收回执','ORPHAN':'游离实收','ATTACH_CONFLICT':'预约版本冲突',
    'AMOUNT':'金额无效','UNKNOWN_SENSOR':'杆侧来源缺失','NONE':'无占位',
    'NEW_STOP':'新停靠出账','UNCHANGED':'与上一批次一致','MERGED':'迟到杆侧记录并入，首免不重复发放',
    'EXTENDED':'迟到记录延长停靠','SPAN_CHANGED':'停靠区间变化','SPLIT':'原停靠拆段，差额随首段结算',
    'REPRICED':'预约内首免额度重分配','VOIDED':'记录移除，原账冲回',
}
