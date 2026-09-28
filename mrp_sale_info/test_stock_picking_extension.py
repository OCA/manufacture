#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证mrp_sale_info模块对拣货单据的销售信息扩展功能
"""

import sys
import os

# 添加odoo路径
sys.path.append('/home/max/projects/odoo-core')

import odoo
from odoo.tools import config

def test_stock_picking_extension():
    """测试拣货单据销售信息扩展功能"""
    
    # 初始化Odoo环境
    config['db_name'] = 'test_db'  # 替换为实际的测试数据库
    odoo.tools.config.parse_config([])
    
    registry = odoo.registry(config['db_name'])
    
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        
        # 测试1：检查模型字段是否存在
        picking_model = env['stock.picking']
        
        # 检查相关字段是否已添加
        assert hasattr(picking_model, 'partner_id'), "partner_id字段不存在"
        assert hasattr(picking_model, 'commitment_date'), "commitment_date字段不存在"
        assert hasattr(picking_model, 'client_order_ref'), "client_order_ref字段不存在"
        
        print("✓ 模型字段检查通过")
        
        # 测试2：检查视图扩展
        # 查找扩展的视图
        tree_view = env.ref('mrp_sale_info.stock_picking_tree_view_inherit', raise_if_not_found=False)
        form_view = env.ref('mrp_sale_info.stock_picking_form_view_inherit', raise_if_not_found=False)
        search_view = env.ref('mrp_sale_info.view_picking_internal_search_inherit', raise_if_not_found=False)
        kanban_view = env.ref('mrp_sale_info.stock_picking_kanban_view_inherit', raise_if_not_found=False)
        
        assert tree_view is not None, "树状视图扩展不存在"
        assert form_view is not None, "表单视图扩展不存在"
        assert search_view is not None, "搜索视图扩展不存在"
        assert kanban_view is not None, "看板视图扩展不存在"
        
        print("✓ 视图扩展检查通过")
        
        # 测试3：检查搜索功能
        # 创建一个测试拣货单据
        test_picking = env['stock.picking'].create({
            'name': 'TEST_PICKING_001',
            'picking_type_id': env.ref('stock.picking_type_out').id,
            'location_id': env.ref('stock.stock_location_stock').id,
            'location_dest_id': env.ref('stock.stock_location_customers').id,
        })
        
        # 测试搜索功能（需要关联销售订单才能测试客户参考号搜索）
        search_result = picking_model._name_search('TEST_PICKING_001')
        assert len(search_result) > 0, "基本搜索功能异常"
        
        print("✓ 搜索功能检查通过")
        
        print("\n🎉 所有测试通过！拣货单据销售信息扩展功能正常。")
        
        # 清理测试数据
        test_picking.unlink()

if __name__ == "__main__":
    try:
        test_stock_picking_extension()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)