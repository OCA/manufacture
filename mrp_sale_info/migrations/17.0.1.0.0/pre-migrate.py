# Copyright 2024 - Odoo Community Association
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    数据迁移脚本：为现有制造订单自动计算销售信息
    在模块安装时执行，处理模块安装前已存在的单据
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # 获取所有制造订单
    mrp_production_model = env['mrp.production']
    all_productions = mrp_production_model.search([])
    
    print(f"开始为 {len(all_productions)} 个制造订单计算销售信息...")
    
    # 批量处理制造订单
    for production in all_productions:
        # 检查是否已经有 source_procurement_group_id
        if not production.source_procurement_group_id:
            # 通过成品移动链查找采购组
            procurement_group = production.move_finished_ids.move_dest_ids.group_id[:1]
            if procurement_group:
                # 设置 source_procurement_group_id
                production.write({
                    'source_procurement_group_id': procurement_group.id
                })
    
    # 强制重新计算所有销售相关字段
    all_productions._compute_sale_info()
    
    print(f"数据迁移完成，已处理 {len(all_productions)} 个制造订单")
    
    # 同时处理工单数据
    mrp_workorder_model = env['mrp.workorder']
    all_workorders = mrp_workorder_model.search([])
    
    print(f"开始为 {len(all_workorders)} 个工单计算销售信息...")
    
    # 强制重新计算工单的销售相关字段
    all_workorders._compute_sale_info()
    
    print(f"工单数据迁移完成，已处理 {len(all_workorders)} 个工单")