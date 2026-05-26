-- =============================================
-- 超市管理系统 - 完整数据库建表语句（合并版）
-- 包含商品/供应商/会员/员工/销售/仓库/财务/系统管理全模块
-- 员工管理模块已严格参照 DFD 1.3 补充并优化
-- =============================================

-- 1. 供应商表 (Supplier)
CREATE TABLE `suppliers` (
    `supplier_id`       INT PRIMARY KEY AUTO_INCREMENT COMMENT '供应商ID (PK)',
    `supplier_name`     VARCHAR(100) NOT NULL COMMENT '供应商名称',
    `contact_person`    VARCHAR(50)  COMMENT '联系人',
    `phone`             VARCHAR(20)  COMMENT '联系电话',
    `address`           VARCHAR(200) COMMENT '地址',
    `credit_level`      VARCHAR(20)  COMMENT '信用等级',
    `created_at`        DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_supplier_name (`supplier_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商表';

-- 2. 商品分类表 (Category)
CREATE TABLE `categories` (
    `category_id`       INT PRIMARY KEY AUTO_INCREMENT COMMENT '分类ID (PK)',
    `category_name`     VARCHAR(80) NOT NULL COMMENT '分类名称',
    `parent_category_id` INT NULL COMMENT '父分类ID (FK，支持多级)',
    `description`       TEXT COMMENT '描述',
    `sort_order`        INT DEFAULT 0 COMMENT '排序号',
    `created_at`        DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`parent_category_id`) REFERENCES `categories`(`category_id`) ON DELETE SET NULL,
    INDEX idx_category_name (`category_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品分类表';

-- 3. 商品表 (Product) - 核心表
CREATE TABLE `products` (
    `product_id`        INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品ID (PK)',
    `product_name`      VARCHAR(150) NOT NULL COMMENT '商品名称',
    `description`       TEXT COMMENT '商品描述',
    `category_id`       INT NOT NULL COMMENT '分类ID (FK)',
    `supplier_id`       INT NOT NULL COMMENT '供应商ID (FK)',
    `base_price`        DECIMAL(12,2) NOT NULL COMMENT '基础价格',
    `spec`              VARCHAR(255) COMMENT '规格/型号',
    `unit`              VARCHAR(20) COMMENT '单位',
    `status`            ENUM('active','inactive','discontinued') DEFAULT 'active' COMMENT '状态：在售/下架/停产',
    `created_at`        DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`category_id`) ON DELETE RESTRICT,
    FOREIGN KEY (`supplier_id`) REFERENCES `suppliers`(`supplier_id`) ON DELETE RESTRICT,
    INDEX idx_product_name (`product_name`),
    INDEX idx_category (`category_id`),
    INDEX idx_supplier (`supplier_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 4. 仓库表 (Warehouse)
CREATE TABLE `warehouses` (
    `warehouse_id`      INT PRIMARY KEY AUTO_INCREMENT COMMENT '仓库ID (PK)',
    `warehouse_name`    VARCHAR(100) NOT NULL COMMENT '仓库名称',
    `location`          VARCHAR(200) COMMENT '位置',
    `capacity`          INT COMMENT '容量',
    `status`            ENUM('active','full','maintenance') DEFAULT 'active',
    `created_at`        DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_warehouse_name (`warehouse_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='仓库表';

-- 5. 库存记录表 (Inventory)
CREATE TABLE `inventory` (
    `inventory_id`      INT PRIMARY KEY AUTO_INCREMENT COMMENT '库存ID (PK)',
    `product_id`        INT NOT NULL COMMENT '商品ID (FK)',
    `warehouse_id`      INT NOT NULL COMMENT '仓库ID (FK)',
    `stock_quantity`    INT NOT NULL DEFAULT 0 COMMENT '当前库存量',
    `safety_stock`      INT NOT NULL DEFAULT 10 COMMENT '安全库存量',
    `last_restock_date` DATETIME COMMENT '最后入库时间',
    `status`            ENUM('normal','low','out_of_stock') DEFAULT 'normal' COMMENT '状态',
    `created_at`        DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`product_id`)   REFERENCES `products`(`product_id`) ON DELETE CASCADE,
    FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses`(`warehouse_id`) ON DELETE RESTRICT,
    INDEX idx_product_warehouse (`product_id`,`warehouse_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存记录表';

-- 6. 商品价格表 (ProductPrice)
CREATE TABLE `product_prices` (
    `price_id`            INT PRIMARY KEY AUTO_INCREMENT COMMENT '价格ID (PK)',
    `product_id`          INT NOT NULL COMMENT '商品ID (FK)',
    `price_type`          ENUM('cost','retail','member','promotion') NOT NULL COMMENT '价格类型',
    `price_value`         DECIMAL(12,2) NOT NULL COMMENT '价格值',
    `effective_start_date` DATE NOT NULL COMMENT '生效开始日期',
    `effective_end_date`   DATE NULL COMMENT '生效结束日期',
    `is_current`          BOOLEAN DEFAULT FALSE COMMENT '是否当前价格',
    `created_at`          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`) ON DELETE CASCADE,
    INDEX idx_product_price (`product_id`),
    INDEX idx_current_price (`product_id`,`is_current`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品价格表';

-- 7. 促销活动表 (Promotion)
CREATE TABLE `promotions` (
    `promotion_id`   INT PRIMARY KEY AUTO_INCREMENT COMMENT '促销ID (PK)',
    `promotion_name` VARCHAR(120) NOT NULL COMMENT '促销名称',
    `promotion_type` ENUM('discount','full_reduction','buy_gift','points') NOT NULL COMMENT '促销类型',
    `discount_rate`  DECIMAL(5,4) NULL COMMENT '折扣率 (如 0.85)',
    `fixed_amount`   DECIMAL(12,2) NULL COMMENT '固定减免金额',
    `start_date`     DATETIME NOT NULL COMMENT '开始日期',
    `end_date`       DATETIME NOT NULL COMMENT '结束日期',
    `approved_by`    INT COMMENT '审批人ID (FK)',
    `status`         ENUM('pending','active','ended','cancelled') DEFAULT 'pending' COMMENT '状态',
    `created_at`     DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_promotion_date (`start_date`,`end_date`),
    INDEX idx_promotion_status (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='促销活动表';

-- 8. 促销商品关联表 (PromotionProduct)
CREATE TABLE `promotion_products` (
    `promotion_id`   INT NOT NULL COMMENT '促销ID (FK)',
    `product_id`     INT NOT NULL COMMENT '商品ID (FK)',
    `specific_discount` DECIMAL(5,4) NULL COMMENT '该商品专属折扣',
    `created_at`     DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`promotion_id`, `product_id`),
    FOREIGN KEY (`promotion_id`) REFERENCES `promotions`(`promotion_id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`)   REFERENCES `products`(`product_id`) ON DELETE CASCADE,
    INDEX idx_promotion (`promotion_id`),
    INDEX idx_product (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='促销商品关联表（M:N 中间表）';

-- ==================== 员工管理模块（已优化合并） ====================

-- 9. 岗位表 (Position) —— 新增，对应 D3.2 岗位信息文件
CREATE TABLE `positions` (
    `position_id`      INT PRIMARY KEY AUTO_INCREMENT COMMENT '岗位ID (PK)',
    `position_name`    VARCHAR(80) NOT NULL COMMENT '岗位名称',
    `responsibilities` TEXT COMMENT '职责描述',
    `permission_level` VARCHAR(50) COMMENT '权限等级',
    `salary_grade`     VARCHAR(20) COMMENT '薪资等级',
    `created_at`       DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`       DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_position_name (`position_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='岗位表';

-- 10. 员工表（已优化合并）—— 重点增强员工属性
CREATE TABLE `employees` (
    `employee_id`   INT PRIMARY KEY AUTO_INCREMENT COMMENT '员工ID (PK)',
    `employee_name` VARCHAR(50)  NOT NULL COMMENT '员工姓名',
    `employee_no`   VARCHAR(20)  NOT NULL UNIQUE COMMENT '工号',
    `id_card`       VARCHAR(18)  COMMENT '身份证号',
    `department`    VARCHAR(50)  COMMENT '部门',
    `position_id`   INT          COMMENT '当前岗位ID (FK)',
    `phone`         VARCHAR(20)  COMMENT '联系电话',
    `email`         VARCHAR(100) COMMENT '邮箱',
    `status`        ENUM('active','inactive','resigned') DEFAULT 'active' COMMENT '状态',
    `hire_date`     DATE COMMENT '入职日期',
    `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`position_id`) REFERENCES `positions`(`position_id`) ON DELETE SET NULL,
    INDEX idx_employee_no (`employee_no`),
    INDEX idx_position (`position_id`),
    INDEX idx_department (`department`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='员工表';

-- 11. 供应商合同表（原sql.txt）
CREATE TABLE `supplier_contracts` (
    `contract_id`    INT PRIMARY KEY AUTO_INCREMENT COMMENT '合同ID (PK)',
    `supplier_id`    INT NOT NULL COMMENT '供应商ID (FK)',
    `contract_number` VARCHAR(50) NOT NULL UNIQUE COMMENT '合同编号',
    `contract_type`  VARCHAR(50) COMMENT '合同类型',
    `start_date`     DATE NOT NULL COMMENT '开始日期',
    `end_date`       DATE NOT NULL COMMENT '结束日期',
    `total_amount`   DECIMAL(15,2) COMMENT '合同总金额',
    `status`         ENUM('pending','approved','active','terminated','expired') DEFAULT 'pending' COMMENT '合同状态',
    `approved_by`    INT COMMENT '审批人ID (FK)',
    `signed_date`    DATE COMMENT '签订日期',
    `created_at`     DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`supplier_id`) REFERENCES `suppliers`(`supplier_id`) ON DELETE RESTRICT,
    FOREIGN KEY (`approved_by`) REFERENCES `employees`(`employee_id`) ON DELETE SET NULL,
    INDEX idx_contract_number (`contract_number`),
    INDEX idx_supplier_contract (`supplier_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商合同表';

-- 12. 供应商评价表（原sql.txt）
CREATE TABLE `supplier_evaluations` (
    `evaluation_id`   INT PRIMARY KEY AUTO_INCREMENT COMMENT '评价ID (PK)',
    `supplier_id`     INT NOT NULL COMMENT '供应商ID (FK)',
    `evaluator_id`    INT NOT NULL COMMENT '评价人ID (FK)',
    `score`           DECIMAL(4,2) NOT NULL COMMENT '总评分',
    `quality_score`   DECIMAL(4,2) COMMENT '质量评分',
    `delivery_score`  DECIMAL(4,2) COMMENT '交付评分',
    `service_score`   DECIMAL(4,2) COMMENT '服务评分',
    `evaluation_date` DATE NOT NULL COMMENT '评价日期',
    `comments`        TEXT COMMENT '评价内容',
    `created_at`      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`supplier_id`)  REFERENCES `suppliers`(`supplier_id`) ON DELETE CASCADE,
    FOREIGN KEY (`evaluator_id`) REFERENCES `employees`(`employee_id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='供应商评价表';

-- 13. 采购订单表（原sql.txt）
CREATE TABLE `purchase_orders` (
    `order_id`       INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID (PK)',
    `supplier_id`    INT NOT NULL COMMENT '供应商ID (FK)',
    `contract_id`    INT NULL COMMENT '关联合同ID (FK)',
    `order_number`   VARCHAR(50) NOT NULL UNIQUE COMMENT '订单编号',
    `order_date`     DATE NOT NULL COMMENT '订单日期',
    `total_amount`   DECIMAL(15,2) NOT NULL COMMENT '订单总金额',
    `status`         ENUM('draft','pending','approved','shipped','received','completed','cancelled') DEFAULT 'draft' COMMENT '订单状态',
    `delivery_date`  DATE COMMENT '预计到货日期',
    `warehouse_id`   INT COMMENT '入库仓库ID (FK)',
    `created_by`     INT COMMENT '创建人 (FK)',
    `approved_by`    INT COMMENT '审批人 (FK)',
    `created_at`     DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`supplier_id`)  REFERENCES `suppliers`(`supplier_id`),
    FOREIGN KEY (`contract_id`)  REFERENCES `supplier_contracts`(`contract_id`),
    FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses`(`warehouse_id`),
    FOREIGN KEY (`created_by`)   REFERENCES `employees`(`employee_id`),
    FOREIGN KEY (`approved_by`)  REFERENCES `employees`(`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采购订单表';

-- 14. 采购订单明细表（原sql.txt）
CREATE TABLE `purchase_order_items` (
    `order_id`     INT NOT NULL COMMENT '订单ID (FK)',
    `product_id`   INT NOT NULL COMMENT '商品ID (FK)',
    `quantity`     INT NOT NULL COMMENT '数量',
    `unit_price`   DECIMAL(12,2) NOT NULL COMMENT '单价',
    `subtotal`     DECIMAL(15,2) NOT NULL COMMENT '小计',
    `created_at`   DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`order_id`, `product_id`),
    FOREIGN KEY (`order_id`)   REFERENCES `purchase_orders`(`order_id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='采购订单明细表';

-- 15. 操作日志表（原sql.txt）
CREATE TABLE `operation_logs` (
    `log_id`        BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID (PK)',
    `module`        VARCHAR(50)  NOT NULL COMMENT '模块名称（如 supplier、contract、evaluation、order、product）',
    `operation`     VARCHAR(100) NOT NULL COMMENT '操作类型（如 create、update、approve、evaluate、delete）',
    `target_id`     INT COMMENT '目标记录ID',
    `target_type`   VARCHAR(50) COMMENT '目标类型',
    `operator_id`   INT NOT NULL COMMENT '操作人ID (FK)',
    `details`       TEXT COMMENT '操作详细内容',
    `ip_address`    VARCHAR(45) COMMENT '操作人IP地址',
    `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    FOREIGN KEY (`operator_id`) REFERENCES `employees`(`employee_id`) ON DELETE RESTRICT,
    INDEX idx_module (`module`),
    INDEX idx_operator (`operator_id`),
    INDEX idx_created_at (`created_at`),
    INDEX idx_target (`target_id`, `target_type`),
    INDEX idx_module_target (`module`, `target_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表（统一记录审批、录入、评价等操作）';

-- ==================== 员工管理模块补充表（D3.3、D3.4） ====================

-- 16. 排班表 (Schedule) —— 对应 D3.3 排班与考勤文件
CREATE TABLE `schedules` (
    `schedule_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '排班ID (PK)',
    `employee_id` INT NOT NULL COMMENT '员工ID (FK)',
    `work_date`   DATE NOT NULL COMMENT '工作日期',
    `shift_type`  ENUM('morning','afternoon','night','rest') NOT NULL COMMENT '班次类型',
    `start_time`  TIME COMMENT '开始时间',
    `end_time`    TIME COMMENT '结束时间',
    `created_by`  INT COMMENT '创建人 (FK)',
    `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`) ON DELETE CASCADE,
    FOREIGN KEY (`created_by`)  REFERENCES `employees`(`employee_id`) ON DELETE SET NULL,
    INDEX idx_employee_workdate (`employee_id`,`work_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='排班表';

-- 17. 考勤记录表 (Attendance) —— 对应 D3.3
CREATE TABLE `attendances` (
    `attendance_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '考勤ID (PK)',
    `employee_id`   INT NOT NULL COMMENT '员工ID (FK)',
    `schedule_id`   INT COMMENT '排班ID (FK)',
    `check_in_time` DATETIME COMMENT '签到时间',
    `check_out_time` DATETIME COMMENT '签退时间',
    `status`        ENUM('normal','late','early','absent','leave') NOT NULL COMMENT '考勤状态',
    `leave_type`    ENUM('casual','sick','annual','other') NULL COMMENT '请假类型',
    `remarks`       TEXT COMMENT '备注',
    `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`) ON DELETE CASCADE,
    FOREIGN KEY (`schedule_id`) REFERENCES `schedules`(`schedule_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考勤记录表';

-- 18. 工资记录表 (Payroll) —— 对应 D3.4 工资核算文件
CREATE TABLE `payrolls` (
    `payroll_id`   INT PRIMARY KEY AUTO_INCREMENT COMMENT '工资ID (PK)',
    `employee_id`  INT NOT NULL COMMENT '员工ID (FK)',
    `pay_period`   VARCHAR(10) NOT NULL COMMENT '工资周期（如 2026-05）',
    `base_salary`  DECIMAL(12,2) NOT NULL COMMENT '基本工资',
    `bonus`        DECIMAL(12,2) DEFAULT 0 COMMENT '奖金/绩效',
    `deduction`    DECIMAL(12,2) DEFAULT 0 COMMENT '扣款',
    `net_pay`      DECIMAL(12,2) NOT NULL COMMENT '实发工资',
    `status`       ENUM('pending','paid','cancelled') DEFAULT 'pending' COMMENT '状态',
    `generated_by` INT COMMENT '生成人 (FK)',
    `created_at`   DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`) ON DELETE CASCADE,
    FOREIGN KEY (`generated_by`) REFERENCES `employees`(`employee_id`) ON DELETE SET NULL,
    INDEX idx_employee_period (`employee_id`,`pay_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='工资记录表';



-- ==================== 会员基础表（为销售模块FK完整性补全，严格参照DFD 1.2 D2.1） ====================
-- 19. 会员表 (Members)
CREATE TABLE `members` (
    `member_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '会员ID (PK)',
    `member_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '会员卡号',
    `member_name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `phone` VARCHAR(20) COMMENT '联系电话',
    `email` VARCHAR(100) COMMENT '邮箱',
    `level` VARCHAR(20) DEFAULT '普通会员' COMMENT '会员等级',
    `points` INT DEFAULT 0 COMMENT '积分余额',
    `register_date` DATE COMMENT '注册日期',
    `status` ENUM('active','inactive','blacklisted') DEFAULT 'active' COMMENT '状态',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_member_no (`member_no`),
    INDEX idx_phone (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员表';

-- ==================== 销售管理模块（基于 Level 2 DFD 1.4 销售管理 完全一致风格） ====================
-- 20. 销售订单表 (Sales Orders) —— D4.1
CREATE TABLE `sales_orders` (
    `order_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID (PK)',
    `order_number` VARCHAR(50) NOT NULL UNIQUE COMMENT '订单编号',
    `member_id` INT COMMENT '会员ID (FK，可空)',
    `employee_id` INT NOT NULL COMMENT '收银员ID (FK)',
    `total_amount` DECIMAL(15,2) NOT NULL COMMENT '订单总金额',
    `payment_method` VARCHAR(30) COMMENT '支付方式',
    `order_date` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '订单时间',
    `status` ENUM('pending','completed','cancelled','refunded') DEFAULT 'pending' COMMENT '订单状态',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`member_id`) REFERENCES `members`(`member_id`) ON DELETE SET NULL,
    FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`),
    INDEX idx_order_number (`order_number`),
    INDEX idx_employee (`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售订单表';

-- 21. 销售订单明细表 (Sales Order Items)
CREATE TABLE `sales_order_items` (
    `order_id` INT NOT NULL COMMENT '订单ID (FK)',
    `product_id` INT NOT NULL COMMENT '商品ID (FK)',
    `quantity` INT NOT NULL COMMENT '数量',
    `unit_price` DECIMAL(12,2) NOT NULL COMMENT '单价',
    `subtotal` DECIMAL(15,2) NOT NULL COMMENT '小计金额',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`order_id`, `product_id`),
    FOREIGN KEY (`order_id`) REFERENCES `sales_orders`(`order_id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`),
    INDEX idx_product (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售订单明细表';

-- 22. 销售退货表 (Sales Returns) —— D4.2
CREATE TABLE `sales_returns` (
    `return_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '退货ID (PK)',
    `original_order_id` INT NOT NULL COMMENT '原订单ID (FK)',
    `member_id` INT COMMENT '会员ID (FK)',
    `employee_id` INT NOT NULL COMMENT '处理人ID (FK)',
    `return_amount` DECIMAL(15,2) NOT NULL COMMENT '退款金额',
    `reason` TEXT COMMENT '退货原因',
    `return_date` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '退货时间',
    `status` ENUM('pending','approved','completed','rejected') DEFAULT 'pending' COMMENT '退货状态',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`original_order_id`) REFERENCES `sales_orders`(`order_id`),
    FOREIGN KEY (`member_id`) REFERENCES `members`(`member_id`) ON DELETE SET NULL,
    FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售退货表';

-- 23. 销售退货明细表 (Sales Return Items)
CREATE TABLE `sales_return_items` (
    `return_id` INT NOT NULL COMMENT '退货ID (FK)',
    `product_id` INT NOT NULL COMMENT '商品ID (FK)',
    `quantity` INT NOT NULL COMMENT '退货数量',
    `refund_amount` DECIMAL(12,2) NOT NULL COMMENT '退款金额',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`return_id`, `product_id`),
    FOREIGN KEY (`return_id`) REFERENCES `sales_returns`(`return_id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售退货明细表';

-- 24. 销售统计表 (Sales Statistics) —— D4.3
CREATE TABLE `sales_statistics` (
    `stat_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '统计ID (PK)',
    `stat_period` VARCHAR(20) NOT NULL COMMENT '统计周期（如 2026-05、日、周）',
    `total_amount` DECIMAL(15,2) NOT NULL COMMENT '销售总额',
    `order_count` INT NOT NULL COMMENT '订单数量',
    `product_count` INT NOT NULL COMMENT '商品种类数',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stat_period (`stat_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='销售统计表';

-- 25. 商品销售排行表 (Product Sales Ranking) —— D4.4
CREATE TABLE `product_sales_rankings` (
    `rank_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '排行ID (PK)',
    `product_id` INT NOT NULL COMMENT '商品ID (FK)',
    `sales_quantity` INT NOT NULL COMMENT '销售数量',
    `sales_amount` DECIMAL(15,2) NOT NULL COMMENT '销售金额',
    `rank_period` VARCHAR(20) NOT NULL COMMENT '排行周期',
    `rank_position` INT COMMENT '排行名次',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`),
    INDEX idx_rank_period (`rank_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品销售排行表';


-- ==================== 会员管理模块补充建表语句（基于 2级 DFD 1.2 会员管理） ====================
-- 风格与 sql.txt 完全一致
-- =============================================

-- 26. 会员等级表 (MemberLevel) —— 对应 D2.2 会员等级文件
CREATE TABLE `member_levels` (
    `level_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '等级ID (PK)',
    `level_name` VARCHAR(50) NOT NULL COMMENT '等级名称（如普通会员、银卡、金卡）',
    `upgrade_condition` VARCHAR(200) COMMENT '升级条件',
    `discount_rate` DECIMAL(5,4) COMMENT '折扣率',
    `points_multiplier` DECIMAL(5,2) DEFAULT 1.00 COMMENT '积分倍率',
    `description` TEXT COMMENT '等级描述',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_level_name (`level_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员等级表';

-- 27. 会员积分记录表 (MemberPointsRecord) —— 对应 D2.3 会员积分记录文件
CREATE TABLE `member_points_records` (
    `record_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID (PK)',
    `member_id` INT NOT NULL COMMENT '会员ID (FK)',
    `points_change` INT NOT NULL COMMENT '积分变化（正数增加，负数减少）',
    `change_type` ENUM('consume','redeem','activity','adjust','refund') NOT NULL COMMENT '变化类型',
    `related_order_id` INT NULL COMMENT '关联销售订单ID',
    `change_date` DATETIME NOT NULL COMMENT '发生日期',
    `remarks` TEXT COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `created_by` INT COMMENT '操作人ID (FK)',
   
    FOREIGN KEY (`member_id`) REFERENCES `members`(`member_id`) ON DELETE CASCADE,
    FOREIGN KEY (`related_order_id`) REFERENCES `sales_orders`(`order_id`) ON DELETE SET NULL,
    FOREIGN KEY (`created_by`) REFERENCES `employees`(`employee_id`) ON DELETE SET NULL,
    INDEX idx_member_points (`member_id`),
    INDEX idx_change_date (`change_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员积分记录表';

-- 28. 积分政策表 (PointsPolicy) —— 对应 D2.4 积分政策文件
CREATE TABLE `points_policies` (
    `policy_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '政策ID (PK)',
    `policy_name` VARCHAR(100) NOT NULL COMMENT '政策名称',
    `earn_rule` TEXT COMMENT '积分获取规则',
    `redeem_rule` TEXT COMMENT '积分兑换规则',
    `valid_period` INT COMMENT '有效期（天）',
    `status` ENUM('active','inactive') DEFAULT 'active' COMMENT '状态',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_policy_name (`policy_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='积分政策表';

-- 29. 会员等级与积分政策关联表（M:N）—— 支持DFD中等级与政策灵活关联
CREATE TABLE `member_level_policies` (
    `level_id` INT NOT NULL COMMENT '等级ID (FK)',
    `policy_id` INT NOT NULL COMMENT '政策ID (FK)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`level_id`, `policy_id`),
    FOREIGN KEY (`level_id`) REFERENCES `member_levels`(`level_id`) ON DELETE CASCADE,
    FOREIGN KEY (`policy_id`) REFERENCES `points_policies`(`policy_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会员等级与积分政策关联表';





-- ==================== 仓库管理模块补充建表语句（基于 2级 DFD 1.6 仓库管理） ====================
-- 严格对应 D6.1~D6.4 数据存储 + 1.6.1~1.6.5 过程
-- 风格与 sql.txt 完全一致
-- =============================================

-- 30. 库存明细表（详细版，对应 D6.2 库存明细文件）
-- 包含批次、库位、有效期，支持现代仓库批次管理
CREATE TABLE `inventory_details` (
    `inventory_detail_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '库存明细ID (PK)',
    `warehouse_id` INT NOT NULL COMMENT '仓库ID (FK)',
    `product_id` INT NOT NULL COMMENT '商品ID (FK)',
    `batch_no` VARCHAR(50) COMMENT '商品批次号',
    `quantity` INT NOT NULL DEFAULT 0 COMMENT '当前数量',
    `bin_location` VARCHAR(50) COMMENT '库位/货架位置',
    `expiry_date` DATE COMMENT '有效期/过期日期',
    `last_movement_date` DATETIME COMMENT '最后移动时间',
    `status` ENUM('normal','low_stock','near_expiry','expired') DEFAULT 'normal' COMMENT '库存状态',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   
    FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses`(`warehouse_id`) ON DELETE RESTRICT,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`) ON DELETE RESTRICT,
    INDEX idx_warehouse_product (`warehouse_id`,`product_id`),
    INDEX idx_batch (`batch_no`),
    INDEX idx_expiry (`expiry_date`),
    INDEX idx_status (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='库存明细表（详细批次/库位/有效期）';

-- 31. 入库记录表（头表，对应 D6.3 入库记录文件 + 1.6.2 商品入库管理）
CREATE TABLE `inbound_records` (
    `inbound_record_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '入库记录ID (PK)',
    `inbound_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '入库单号',
    `supplier_id` INT NOT NULL COMMENT '供应商ID (FK)',
    `warehouse_id` INT NOT NULL COMMENT '仓库ID (FK)',
    `total_quantity` INT NOT NULL DEFAULT 0 COMMENT '总数量',
    `inbound_date` DATETIME NOT NULL COMMENT '入库时间',
    `status` ENUM('pending','inspecting','received','completed','cancelled') DEFAULT 'pending' COMMENT '入库状态',
    `created_by` INT NOT NULL COMMENT '创建人ID (FK)',
    `notes` TEXT COMMENT '备注/验收记录',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   
    FOREIGN KEY (`supplier_id`) REFERENCES `suppliers`(`supplier_id`),
    FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses`(`warehouse_id`),
    FOREIGN KEY (`created_by`) REFERENCES `employees`(`employee_id`),
    INDEX idx_inbound_no (`inbound_no`),
    INDEX idx_supplier (`supplier_id`),
    INDEX idx_warehouse (`warehouse_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库记录表（头表）';

-- 32. 入库明细表（对应入库记录的商品列表）
CREATE TABLE `inbound_items` (
    `inbound_record_id` INT NOT NULL COMMENT '入库记录ID (FK)',
    `product_id` INT NOT NULL COMMENT '商品ID (FK)',
    `batch_no` VARCHAR(50) COMMENT '商品批次号',
    `quantity` INT NOT NULL COMMENT '入库数量',
    `unit_price` DECIMAL(12,2) COMMENT '单价（可选）',
    `expiry_date` DATE COMMENT '有效期',
    `bin_location` VARCHAR(50) COMMENT '入库库位',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
   
    PRIMARY KEY (`inbound_record_id`, `product_id`, `batch_no`),
    FOREIGN KEY (`inbound_record_id`) REFERENCES `inbound_records`(`inbound_record_id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`),
    INDEX idx_product (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='入库明细表（商品列表）';

-- 33. 出库记录表（头表，对应 D6.4 出库记录文件 + 1.6.3 商品出库管理）
CREATE TABLE `outbound_records` (
    `outbound_record_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '出库记录ID (PK)',
    `outbound_no` VARCHAR(50) NOT NULL UNIQUE COMMENT '出库单号',
    `source_order_id` INT COMMENT '来源销售订单ID (FK，可空)',
    `warehouse_id` INT NOT NULL COMMENT '仓库ID (FK)',
    `total_quantity` INT NOT NULL DEFAULT 0 COMMENT '总数量',
    `outbound_date` DATETIME NOT NULL COMMENT '出库时间',
    `status` ENUM('pending','picking','shipped','completed','cancelled') DEFAULT 'pending' COMMENT '出库状态',
    `created_by` INT NOT NULL COMMENT '创建人ID (FK)',
    `notes` TEXT COMMENT '备注',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   
    FOREIGN KEY (`source_order_id`) REFERENCES `sales_orders`(`order_id`) ON DELETE SET NULL,
    FOREIGN KEY (`warehouse_id`) REFERENCES `warehouses`(`warehouse_id`),
    FOREIGN KEY (`created_by`) REFERENCES `employees`(`employee_id`),
    INDEX idx_outbound_no (`outbound_no`),
    INDEX idx_source_order (`source_order_id`),
    INDEX idx_warehouse (`warehouse_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='出库记录表（头表）';

-- 34. 出库明细表（对应出库记录的商品列表）
CREATE TABLE `outbound_items` (
    `outbound_record_id` INT NOT NULL COMMENT '出库记录ID (FK)',
    `product_id` INT NOT NULL COMMENT '商品ID (FK)',
    `batch_no` VARCHAR(50) COMMENT '商品批次号（先进先出可选）',
    `quantity` INT NOT NULL COMMENT '出库数量',
    `bin_location` VARCHAR(50) COMMENT '出库库位',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
   
    PRIMARY KEY (`outbound_record_id`, `product_id`, `batch_no`),
    FOREIGN KEY (`outbound_record_id`) REFERENCES `outbound_records`(`outbound_record_id`) ON DELETE CASCADE,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`product_id`),
    INDEX idx_product (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='出库明细表（商品列表）';


-- =============================================
-- 财务管理模块补充建表语句（基于 2级 DFD 1.7 财务管理）
-- 风格与 sql.txt 完全一致
-- =============================================
-- =============================================
-- 财务管理模块补充建表语句（基于 2级 DFD 1.7 财务管理）
-- 风格与 sql.txt 完全一致，已统一规范化（反引号 + 半角空格 + DFD注释）
-- =============================================

-- 35. 收银记录表 (Cash Records) —— 对应 DFD 1.7 D7.1 收银记录文件
CREATE TABLE `cash_records` (
    `cash_record_id`   INT PRIMARY KEY AUTO_INCREMENT COMMENT '收银记录ID (PK)',
    `order_id`         INT NOT NULL COMMENT '销售订单ID (FK)',
    `employee_id`      INT NOT NULL COMMENT '收银员ID (FK)',
    `amount`           DECIMAL(15,2) NOT NULL COMMENT '收银金额',
    `payment_method`   VARCHAR(30) NOT NULL COMMENT '支付方式',
    `transaction_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '交易时间',
    `status`           ENUM('success','failed','refunded') DEFAULT 'success' COMMENT '状态',
    `created_at`       DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`       DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`order_id`) REFERENCES `sales_orders`(`order_id`) ON DELETE RESTRICT,
    FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`) ON DELETE RESTRICT,
    
    INDEX `idx_order` (`order_id`),
    INDEX `idx_employee` (`employee_id`),
    INDEX `idx_transaction_time` (`transaction_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收银记录表 (D7.1)';

-- 36. 会计科目表 (Accounts) —— 对应 DFD 1.7 D7.2 财务账目文件
CREATE TABLE `accounts` (
    `account_id`    INT PRIMARY KEY AUTO_INCREMENT COMMENT '科目ID (PK)',
    `account_code`  VARCHAR(20) NOT NULL UNIQUE COMMENT '科目编码',
    `account_name`  VARCHAR(100) NOT NULL COMMENT '科目名称',
    `account_type`  ENUM('asset','liability','equity','revenue','expense') NOT NULL COMMENT '科目类型',
    `parent_id`     INT NULL COMMENT '父科目ID (FK，自引用)',
    `balance`       DECIMAL(15,2) DEFAULT 0.00 COMMENT '当前余额',
    `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`    DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`parent_id`) REFERENCES `accounts`(`account_id`) ON DELETE SET NULL,
    
    INDEX `idx_account_code` (`account_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会计科目表 (D7.2)';

-- 37. 会计凭证表 (Journal Entries) —— 对应 DFD 1.7 D7.2
CREATE TABLE `journal_entries` (
    `journal_entry_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '凭证ID (PK)',
    `voucher_no`       VARCHAR(50) NOT NULL UNIQUE COMMENT '凭证号',
    `entry_date`       DATE NOT NULL COMMENT '记账日期',
    `description`      TEXT COMMENT '摘要',
    `total_debit`      DECIMAL(15,2) NOT NULL COMMENT '借方合计',
    `total_credit`     DECIMAL(15,2) NOT NULL COMMENT '贷方合计',
    `created_by`       INT COMMENT '制单人ID (FK)',
    `status`           ENUM('draft','posted','reversed') DEFAULT 'draft' COMMENT '状态',
    `created_at`       DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`       DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`created_by`) REFERENCES `employees`(`employee_id`) ON DELETE SET NULL,
    
    INDEX `idx_voucher_no` (`voucher_no`),
    INDEX `idx_entry_date` (`entry_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会计凭证表 (D7.2)';

-- 38. 会计凭证明细表（借贷分录）—— 对应 DFD 1.7 D7.2
CREATE TABLE `journal_entry_items` (
    `item_id`            INT PRIMARY KEY AUTO_INCREMENT COMMENT '分录ID (PK)',
    `journal_entry_id`   INT NOT NULL COMMENT '凭证ID (FK)',
    `account_id`         INT NOT NULL COMMENT '科目ID (FK)',
    `debit_amount`       DECIMAL(15,2) DEFAULT 0.00 COMMENT '借方金额',
    `credit_amount`      DECIMAL(15,2) DEFAULT 0.00 COMMENT '贷方金额',
    `description`        TEXT COMMENT '分录摘要',
    `created_at`         DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`journal_entry_id`) REFERENCES `journal_entries`(`journal_entry_id`) ON DELETE CASCADE,
    FOREIGN KEY (`account_id`) REFERENCES `accounts`(`account_id`) ON DELETE RESTRICT,
    
    INDEX `idx_journal_entry` (`journal_entry_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会计凭证明细表 (D7.2)';

-- 39. 成本核算记录表 —— 对应 DFD 1.7 D7.3 成本核算文件
CREATE TABLE `cost_records` (
    `cost_record_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '成本记录ID (PK)',
    `cost_type`      ENUM('purchase','inventory','operation','other') NOT NULL COMMENT '成本类型',
    `related_id`     INT COMMENT '关联ID（采购单/商品ID等）',
    `related_type`   VARCHAR(50) COMMENT '关联类型',
    `amount`         DECIMAL(15,2) NOT NULL COMMENT '成本金额',
    `cost_date`      DATE NOT NULL COMMENT '成本发生日期',
    `description`    TEXT COMMENT '描述',
    `created_at`     DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`related_id`) REFERENCES `purchase_orders`(`order_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成本核算记录表 (D7.3)';

-- 40. 预算表 —— 对应 DFD 1.7 D7.4 预算文件
CREATE TABLE `budgets` (
    `budget_id`      INT PRIMARY KEY AUTO_INCREMENT COMMENT '预算ID (PK)',
    `budget_period`  VARCHAR(20) NOT NULL COMMENT '预算期间（如 2026-05）',
    `account_id`     INT NOT NULL COMMENT '科目ID (FK)',
    `planned_amount` DECIMAL(15,2) NOT NULL COMMENT '计划金额',
    `actual_amount`  DECIMAL(15,2) DEFAULT 0.00 COMMENT '实际执行金额',
    `variance`       DECIMAL(15,2) COMMENT '差异',
    `approved_by`    INT COMMENT '审批人ID (FK)',
    `status`         ENUM('draft','approved','executing','closed') DEFAULT 'draft',
    `created_at`     DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`account_id`) REFERENCES `accounts`(`account_id`) ON DELETE RESTRICT,
    FOREIGN KEY (`approved_by`) REFERENCES `employees`(`employee_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预算表 (D7.4)';

-- 41. 税务申报记录表 —— 对应 DFD 1.7 D7.5 税务申报文件
CREATE TABLE `tax_declarations` (
    `tax_declaration_id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '税务申报ID (PK)',
    `tax_type`           VARCHAR(50) NOT NULL COMMENT '税种（如增值税、企业所得税）',
    `declaration_period` VARCHAR(20) NOT NULL COMMENT '申报期间',
    `tax_amount`         DECIMAL(15,2) NOT NULL COMMENT '应纳税额',
    `paid_amount`        DECIMAL(15,2) DEFAULT 0.00 COMMENT '已缴金额',
    `payment_status`     ENUM('unpaid','paid','overdue') DEFAULT 'unpaid',
    `submitted_to`       VARCHAR(100) COMMENT '提交对象（税务局等）',
    `submission_date`    DATE COMMENT '申报日期',
    `created_at`         DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX `idx_declaration_period` (`declaration_period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='税务申报记录表 (D7.5)';


-- =============================================
-- 系统管理模块补充建表语句（基于 2级 DFD 1.8 系统管理）
-- 风格与 sql.txt 完全一致
-- =============================================

-- 42. 用户表 (Users)
CREATE TABLE `users` (
    `user_id`        INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID (PK)',
    `username`       VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `password_hash`  VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `employee_id`    INT NULL COMMENT '关联员工ID (FK)',
    `status`         ENUM('active','inactive','locked') DEFAULT 'active' COMMENT '状态',
    `last_login`     DATETIME COMMENT '最后登录时间',
    `created_at`     DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`     DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`employee_id`) REFERENCES `employees`(`employee_id`) ON DELETE SET NULL,
    INDEX idx_username (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 43. 角色表 (Roles)
CREATE TABLE `roles` (
    `role_id`     INT PRIMARY KEY AUTO_INCREMENT COMMENT '角色ID (PK)',
    `role_name`   VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称',
    `description` TEXT COMMENT '角色描述',
    `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role_name (`role_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- 44. 权限表 (Permissions)
CREATE TABLE `permissions` (
    `permission_id`   INT PRIMARY KEY AUTO_INCREMENT COMMENT '权限ID (PK)',
    `permission_code` VARCHAR(100) NOT NULL UNIQUE COMMENT '权限代码（如 user:create, order:view）',
    `permission_name` VARCHAR(100) NOT NULL COMMENT '权限名称',
    `module`          VARCHAR(50) COMMENT '所属模块',
    `description`     TEXT COMMENT '权限描述',
    `created_at`      DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_permission_code (`permission_code`),
    INDEX idx_module (`module`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- 45. 用户角色关联表 (User Roles - 多对多)
CREATE TABLE `user_roles` (
    `user_id`  INT NOT NULL COMMENT '用户ID (FK)',
    `role_id`  INT NOT NULL COMMENT '角色ID (FK)',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`user_id`, `role_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`role_id`) REFERENCES `roles`(`role_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

-- 46. 角色权限关联表 (Role Permissions - 多对多)
CREATE TABLE `role_permissions` (
    `role_id`       INT NOT NULL COMMENT '角色ID (FK)',
    `permission_id` INT NOT NULL COMMENT '权限ID (FK)',
    `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`role_id`, `permission_id`),
    FOREIGN KEY (`role_id`)       REFERENCES `roles`(`role_id`) ON DELETE CASCADE,
    FOREIGN KEY (`permission_id`) REFERENCES `permissions`(`permission_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';

-- 47. 系统日志表 (System Logs)
CREATE TABLE `system_logs` (
    `log_id`      BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '日志ID (PK)',
    `user_id`     INT COMMENT '操作用户ID (FK)',
    `log_type`    ENUM('operation','login','exception','audit') NOT NULL COMMENT '日志类型',
    `module`      VARCHAR(50) COMMENT '操作模块',
    `action`      VARCHAR(100) COMMENT '操作动作',
    `description` TEXT COMMENT '详细描述',
    `ip_address`  VARCHAR(45) COMMENT 'IP地址',
    `log_time`    DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '日志时间',
    `created_at`  DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE SET NULL,
    INDEX idx_user (`user_id`),
    INDEX idx_log_type (`log_type`),
    INDEX idx_module (`module`),
    INDEX idx_log_time (`log_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统日志表';

-- 48. 备份记录表 (Backup Records)
CREATE TABLE `backup_records` (
    `backup_id`     INT PRIMARY KEY AUTO_INCREMENT COMMENT '备份ID (PK)',
    `backup_type`   ENUM('full','incremental','differential') NOT NULL COMMENT '备份类型',
    `backup_path`   VARCHAR(255) NOT NULL COMMENT '备份路径',
    `backup_size`   BIGINT COMMENT '备份大小（字节）',
    `status`        ENUM('success','failed','in_progress') DEFAULT 'in_progress' COMMENT '状态',
    `executed_by`   INT COMMENT '执行人用户ID (FK)',
    `backup_time`   DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '备份时间',
    `restore_time`  DATETIME COMMENT '恢复时间（可空）',
    `created_at`    DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`executed_by`) REFERENCES `users`(`user_id`) ON DELETE SET NULL,
    INDEX idx_backup_time (`backup_time`),
    INDEX idx_status (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='备份记录表';

-- 49. 系统配置表 (System Configs)
CREATE TABLE `system_configs` (
    `config_id`    INT PRIMARY KEY AUTO_INCREMENT COMMENT '配置ID (PK)',
    `config_key`   VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键（如 system.version, ui.theme）',
    `config_value` TEXT NOT NULL COMMENT '配置值',
    `config_type`  ENUM('system','ui','business') DEFAULT 'system' COMMENT '配置类型',
    `description`  TEXT COMMENT '描述',
    `updated_by`   INT COMMENT '更新人用户ID (FK)',
    `updated_at`   DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (`updated_by`) REFERENCES `users`(`user_id`) ON DELETE SET NULL,
    INDEX idx_config_key (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';
-- =============================================
-- 建表完成提示
-- =============================================
-- 所有表已按逻辑依赖顺序排列，可直接执行。
-- 员工相关表（positions、employees、schedules、attendances、payrolls）已完全对应 DFD 1.3 员工管理模块的数据文件（D3.1~D3.4）。