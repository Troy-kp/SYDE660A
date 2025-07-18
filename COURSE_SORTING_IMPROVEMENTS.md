# 课程池排序改进

## 问题描述
原来的课程池中，课程的排序不够清晰，Required（必修）课程和Core（核心）课程没有按照重要性优先显示，用户难以快速找到最重要的课程。

## 解决方案

### 1. 后端排序逻辑改进 (`src/core/planner.py`)

**新的排序优先级顺序：**
1. **Required** - 必修课程（最高优先级）
2. **Core** - 核心课程 
3. **Choice Required** - 必选课程（从指定课程中选择）
4. **Specified Elective** - 指定选修课程
5. **General Elective** - 一般选修课程（最低优先级）

**改进内容：**
- 修改了 `_course_sort_key` 方法，使用基于标签和类别的智能排序
- 确保Required标签的课程始终显示在最前面
- 在同一优先级内，按课程代码字母顺序排列

### 2. 前端排序逻辑同步 (`web/templates/UserInterface.html`)

**改进内容：**
- 更新了 `renderCoursePool` 函数中的排序逻辑
- 添加了 `getSortPriority` 辅助函数，与后端保持一致
- 确保前后端排序结果完全一致

## 技术细节

### 后端排序算法
```python
def _course_sort_key(self, course_item: Dict) -> Tuple:
    # 主要排序：按课程重要性 (Required → Core → etc.)
    if 'Required' in tags:
        sort_priority = 1  # 最高优先级 - Required课程
    elif category == 'compulsory':
        sort_priority = 2  # 核心必修课程
    elif 'Choice Required' in tags or category == 'compulsory_choice':
        sort_priority = 3  # 必选课程
    elif 'Specified Elective' in tags or category == 'specified_elective':
        sort_priority = 4  # 指定选修课程
    elif 'Elective' in tags or category in ['general_elective', 'elective']:
        sort_priority = 5  # 一般选修课程
    else:
        sort_priority = 6  # 其他课程
    
    # 次要排序：SYDE课程优先，然后按学科字母顺序
    # 三级排序：研究生课程优先
    # 四级排序：同学科内按课程编号数字顺序
```

### 前端排序算法
```javascript
function getSortPriority(item) {
    const tags = item.tags || [];
    const category = item.category;
    
    if (tags.includes('Required')) return 1;           // Required courses first
    if (category === 'compulsory') return 2;           // Core required courses
    if (tags.includes('Choice Required') || category === 'compulsory_choice') return 3;
    if (tags.includes('Specified Elective') || category === 'specified_elective') return 4;
    if (tags.includes('Elective') || ['general_elective', 'elective'].includes(category)) return 5;
    return 6;  // Other courses
}
```

## 预期效果

用户现在可以：
1. **快速找到必修课程** - Required课程显示在最前面
2. **按重要性浏览** - 课程按照学术要求的重要性排序
3. **直观的优先级** - 视觉上更容易理解课程的相对重要性
4. **一致的体验** - 前后端排序完全同步

## 测试验证

可以通过以下方式验证改进：
1. 访问课程规划界面
2. 选择任意专业方向
3. 查看课程池中课程的排列顺序
4. 验证Required课程是否出现在最前面
5. 确认Core课程紧随其后

这个改进显著提升了用户体验，让课程规划变得更加直观和高效。 