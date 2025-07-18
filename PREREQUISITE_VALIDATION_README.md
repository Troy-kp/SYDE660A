# 先修课程验证系统

## 功能概述

我们为SYDE Interactive Course Planner添加了强大的先修课程验证系统，确保用户的课程选择符合学术要求。

## 新增功能

### 1. 增强的先修课程解析器 (EnhancedPrerequisiteParser)

该解析器能够解析课程的`requirementsDescription`字段，提取以下信息：

- **先修课程 (Prerequisites)**: 必须在选修目标课程前完成的课程
- **反修课程 (Antirequisites)**: 与目标课程互斥的课程
- **同修课程 (Corequisites)**: 必须与目标课程同时修读的课程
- **等级要求 (Level Requirements)**: 学术等级要求
- **其他要求**: 导师同意、部门许可等

#### 支持的格式示例

```
Prerequisite: SYDE 600; Antirequisite: SYDE 660A, 660B, 660C, 660D, 660E
Prereq: One of BME 122, ECE 250, MSE 240, MTE 140, SYDE 223; Level at least 4A BASc/BSE
Prereq/coreq: ECE 650 or 750 Tpc 26 or instructor consent
```

### 2. 课程验证器 (CourseValidator)

提供智能的课程放置验证，检查：

- ✅ **先修课程满足**: 确保所需的先修课程已在之前的学期完成
- ❌ **反修课程冲突**: 检测与已完成课程的冲突
- ⚠️ **等级要求**: 验证学术等级要求
- 📅 **开课时间**: 确认课程在目标学期提供

### 3. 学期序列管理器 (TermSequenceManager)

- 管理学期的时间顺序
- 确定哪些课程在目标学期之前完成
- 支持1241-1251格式的学期代码

### 4. 前端用户界面增强

#### 课程卡片显示
- 在课程池中的每张课程卡片下方显示先修、反修、同修信息
- 使用颜色编码区分不同类型的要求：
  - 🔵 先修课程 (蓝色边框)
  - 🔴 反修课程 (红色边框)  
  - 🟡 同修课程 (黄色边框)

#### 实时验证反馈
- 拖拽课程时提供实时验证
- 详细的错误和警告消息
- 智能的课程放置建议

## API端点

### `/api/v1/validate_move` (POST)
验证课程是否可以放置在指定学期

**请求格式:**
```json
{
  "course_code": "SYDE 660",
  "term_code": "1255",
  "current_plan": {
    "1241": ["SYDE 600"],
    "1249": ["SYDE 610"]
  }
}
```

**响应格式:**
```json
{
  "valid": true,
  "issues": [],
  "warnings": ["Verify you meet level requirement: 4A in Computer Engineering"],
  "prerequisite_status": {
    "req_0": {
      "requirement": "SYDE 600",
      "satisfied": true,
      "type": "required",
      "missing_courses": []
    }
  },
  "antirequisite_conflicts": [],
  "requirements_summary": {
    "prerequisites": [...],
    "antirequisites": [...],
    "corequisites": [...]
  }
}
```

### `/api/v1/course_info` (POST)
获取课程的详细信息，包括解析后的先修课程要求

**请求格式:**
```json
{
  "course_code": "SYDE 660"
}
```

## 验证场景示例

### 场景1: 新生尝试选修高级课程
- **情况**: 2025 Spring入学的学生尝试选择SYDE 660
- **结果**: ❌ 失败 - 缺少先修课程SYDE 600
- **消息**: "Prerequisite not satisfied: SYDE 600"

### 场景2: 已满足先修要求
- **情况**: 学生在1241学期完成了SYDE 600，现在想在1255选择SYDE 660
- **结果**: ✅ 成功 - 所有先修要求满足

### 场景3: 反修课程冲突
- **情况**: 学生已经完成SYDE 660A，现在尝试选择SYDE 660
- **结果**: ❌ 失败 - 反修课程冲突
- **消息**: "Antirequisite conflict: Cannot take SYDE 660 if SYDE 660A is completed"

## 技术实现细节

### 正则表达式解析
- 课程代码模式: `\b([A-Z]+)\s*(\d+[A-Z]*)\b`
- 等级要求模式: `Level\s+at\s+least\s+(\d+[A-Z]?)\s+([^.;,]+)`
- 分段解析先修、反修、同修要求

### 验证算法
1. 解析目标课程的要求
2. 收集目标学期之前的所有已完成课程
3. 检查先修课程是否满足
4. 检查反修课程冲突
5. 验证等级和其他要求
6. 生成详细的验证报告

## 未来改进方向

1. **更智能的课程推荐**: 基于先修关系推荐合适的课程序列
2. **可视化依赖图**: 显示课程之间的先修关系图
3. **自动课程排序**: 根据先修关系自动安排最优的课程顺序
4. **历史数据分析**: 基于历史选课数据提供个性化建议
5. **导出功能**: 导出验证报告和课程计划

## 支持的工程专业

当前系统支持以下6个工程专业的先修课程验证：
- Systems Design Engineering (SYDE)
- Electrical and Computer Engineering (ECE)
- Chemical Engineering (CHE)
- Civil and Environmental Engineering (CIVE)
- Mechanical and Mechatronics Engineering (ME)
- Management Science and Engineering (MSE)

每个专业都有完整的课程数据和先修关系解析支持。 