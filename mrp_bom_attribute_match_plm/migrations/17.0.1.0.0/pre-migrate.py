# -*- coding: utf-8 -*-
"""
数据迁移脚本：为已存在的PLM BOM变更记录添加component_template_id字段支持
"""

def migrate(cr, version):
    """
    迁移函数：为已存在的mrp.eco.bom.change记录处理component_template_id字段
    """
    # 检查component_template_id字段是否存在，如果不存在则创建
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'mrp_eco_bom_change' 
        AND column_name = 'component_template_id'
    """)
    
    if not cr.fetchone():
        # 添加component_template_id字段
        cr.execute("""
            ALTER TABLE mrp_eco_bom_change 
            ADD COLUMN component_template_id integer
        """)
        
        # 添加外键约束
        cr.execute("""
            ALTER TABLE mrp_eco_bom_change 
            ADD CONSTRAINT mrp_eco_bom_change_component_template_id_fkey 
            FOREIGN KEY (component_template_id) REFERENCES product_template(id)
        """)
        
        print("已成功添加component_template_id字段到mrp_eco_bom_change表")
    
    # 检查product_backup_id字段是否存在，如果不存在则创建
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'mrp_eco_bom_change' 
        AND column_name = 'product_backup_id'
    """)
    
    if not cr.fetchone():
        # 添加product_backup_id字段
        cr.execute("""
            ALTER TABLE mrp_eco_bom_change 
            ADD COLUMN product_backup_id integer
        """)
        
        # 添加外键约束
        cr.execute("""
            ALTER TABLE mrp_eco_bom_change 
            ADD CONSTRAINT mrp_eco_bom_change_product_backup_id_fkey 
            FOREIGN KEY (product_backup_id) REFERENCES product_product(id)
        """)
        
        print("已成功添加product_backup_id字段到mrp_eco_bom_change表")
    
    # 更新已存在的记录，确保它们与新的字段结构兼容
    # 对于已存在的记录，product_id字段已经包含有效数据
    # component_template_id字段将保持为空，这是正常的
    
    print("数据迁移完成：已存在的PLM BOM变更记录现在支持component_template_id字段")