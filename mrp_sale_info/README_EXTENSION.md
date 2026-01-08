# MRP Sale Info 模块扩展 - 拣货单据销售信息

## 功能概述

本扩展为 `mrp_sale_info` 模块增加了对拣货单据（Stock Picking）的销售信息显示功能，使制造流程中的拣货环节也能关联销售订单信息。

## 新增功能

### 1. 拣货单据模型扩展
- **销售订单关联**: 通过 `sale_stock` 模块已有的 `sale_id` 字段关联销售订单
- **客户信息**: 显示销售订单对应的客户信息
- **承诺日期**: 显示销售订单的承诺交付日期
- **客户参考号**: 显示客户提供的参考编号

### 2. 界面视图扩展

#### 列表视图（Tree View）
- 在 `origin` 字段后添加销售订单、客户、承诺日期、客户参考号字段
- 支持可选显示/隐藏，提高界面灵活性

#### 表单视图（Form View）
- 新增"销售信息"标签页，位于"操作"标签页之后
- 仅对库存管理员（`stock.group_stock_manager`）可见
- 分组显示销售相关信息

#### 搜索视图（Search View）
- 扩展搜索功能，支持按客户参考号搜索
- 搜索域：`['|', '|', ('name', 'ilike', self), ('origin', 'ilike', self), ('client_order_ref', 'ilike', self)]`

#### 看板视图（Kanban View）
- 在看板卡片顶部显示销售订单和客户参考号
- 使用头像组件显示销售订单

### 3. 搜索功能增强
- 支持按客户参考号快速搜索拣货单据
- 扩展 `_name_search` 方法，提供更灵活的搜索体验

## 技术实现

### 模型层 (`models/stock_picking.py`)
```python
class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    # 使用sale_stock模块提供的sale_id字段
    partner_id = fields.Many2one(related="sale_id.partner_id", ...)
    commitment_date = fields.Datetime(related="sale_id.commitment_date", ...)
    client_order_ref = fields.Char(related="sale_id.client_order_ref", ...)
```

### 视图层 (`views/stock_picking.xml`)
- 4个视图扩展记录，分别对应列表、表单、搜索、看板视图
- 使用合理的XPath定位和位置属性
- 遵循Odoo视图继承最佳实践

### 依赖关系
- 继承 `sale_stock` 模块的现有功能
- 无需额外权限配置
- 与现有制造模块无缝集成

## 安装和配置

### 1. 模块安装
```bash
# 在Odoo中安装mrp_sale_info模块
# 模块将自动应用拣货单据扩展功能
```

### 2. 权限配置
- "销售信息"标签页仅对库存管理员可见
- 无需额外权限配置

### 3. 界面配置
用户可以在列表视图中通过可选字段配置显示/隐藏销售相关字段。

## 使用说明

### 1. 查看销售信息
1. 进入 **库存 → 操作 → 调拨**
2. 打开任意拣货单据
3. 查看"销售信息"标签页（库存管理员可见）

### 2. 搜索功能
1. 在拣货单据搜索框中输入：
   - 拣货单据名称
   - 来源单据编号  
   - **客户参考号**（新增功能）

### 3. 列表视图配置
1. 在拣货单据列表页面
2. 点击右上角"可选字段"按钮
3. 选择显示/隐藏销售相关字段

## 兼容性

- **Odoo版本**: 17.0+
- **依赖模块**: `mrp`, `sale_stock`
- **数据库**: PostgreSQL

## 测试验证

运行测试脚本验证功能：
```bash
cd /home/max/projects/odoo-addons/manufacture/mrp_sale_info
python test_stock_picking_extension.py
```

## 扩展建议

### 未来扩展方向
1. **报表功能**: 添加销售相关的拣货统计报表
2. **工作流集成**: 与销售订单工作流深度集成
3. **高级筛选**: 增加更多销售相关的筛选条件
4. **批量操作**: 支持基于销售信息的批量操作

### 性能优化
- 利用ORM的related字段，避免重复计算
- 合理使用索引优化搜索性能
- 视图继承保持轻量级

## 技术支持

如遇问题，请参考：
- Odoo官方文档
- OCA (Odoo Community Association) 指南
- 模块GitHub仓库的Issues页面

---

**版本**: 1.0.0  
**最后更新**: 2024年  
**维护者**: Odoo社区协会 (OCA)