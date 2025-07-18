# Waterloo Course & Schedule Datasets (2021-2025)

## API_course_data_filtered/

本目录保存 **已验证开课** 的课程详情 JSON 文件，结构示例如下：

```
API_course_data_filtered/
# 包含本科 + 研究生课程
  CS/
    1259.json         # CS - Fall 2025 开课课程
    1255.json         # CS - Spring 2025
  MATH/
    1259.json
```

每个 `<TERM>.json` 文件对应「某学期 + 某学科(subject)」**实际排课**的全部课程条目，字段说明见下文表格。

### 生成逻辑
1. **抓取课程表** － 对每个学期调用API接口中 `ClassSchedules/{term}`，得到实际排课的 `courseId` 列表。
2. **抓取课程详情** － 对目录中的每个学科调用API接口中 `Courses/{term}/{subject}`，获取官方课程条目数组。
3. **交叉过滤** － 仅保留 `course['courseId']` 存在于步骤 1 列表中的记录（即确有 section）。
4. **写入文件** － 将过滤后的数组写入本目录相应 `API_schedule_data_filtered/<SUBJECT>/<TERM>.json`。

## 数据范围与完整性

| 维度              | 覆盖情况                |
|-------------------|-------------------------|
| 年份              | 2021 – 2025            |
| 学期数量          | 15 (W,S,F * 5 年)      |
| 课程层次          | 本科 **+** 研究生       |
| 专业 (subject)    | 280+ UW Program |

### 课程对象字段说明

课程 JSON 对象常见字段一览：

| 字段 | 示例 | 含义 |
|------|-------|------|
| `courseId` | `"000602"` | UW 内部唯一 id；与课表文件中的 id 对应，用来判断是否实际排课 |
| `courseOfferNumber` | `1` | 同一课程在同学期若有不同版本/大纲会递增，大多数情况下为 1 |
| `termCode` / `termName` | `"1259" / "Fall 2025"` | 学期代码 / 学期名称 |
| `associatedAcademicCareer` | `"UG" / "GRD"` | 课程层次：UG 本科、GRD 研究生 |
| `associatedAcademicGroupCode` | `"MAT"` | 学院大组代码（例：MAT=数学、ENG=工程） |
| `associatedAcademicOrgCode` | `"CS"` | 开课院系代码，通常与 `subjectCode` 相同 |
| `subjectCode` | `"CS"` | 学科(科目)代码 |
| `catalogNumber` | `"341"`、`"685"` | 与 `subjectCode` 拼接即完整课号：`CS341`, `CS685` |
| `title` | `"Algorithms"` | 课程英文标题 |
| `descriptionAbbreviated` | `"Algorithms"` | 官方缩写描述（≤30 字符） |
| `description` | `"..."` | 课程详细描述 |
| `gradingBasis` | `"NUM"` | 评分方式：NUM=百分制成绩；CNC=Credit/No-credit 等 |
| `courseComponentCode` | `"LEC"` | 授课组成类型：LEC(讲座)、LAB(实验)、SEM(研讨)… |
| `enrollConsentCode` / `enrollConsentDescription` | `"N"` / `"No Consent Required"` | 选课是否需要额外批准 |
| `dropConsentCode` / `dropConsentDescription` | `"N"` / `"No Consent Required"` | 退课是否需要额外批准 |
| `requirementsDescription` | `"Prereq: CS 240…"` 或 `null` | 先修、互斥、限制说明 |

> 注：JSON 中可能还有其他字段，以上为最常用且在推荐系统与数据库建模中会用到的键值。若需完整字段，请查看 UW Open Data `Courses` 端点官方文档。

### TermCode 对照表（2021-2025）

| termCode | 学期 |
|----------|------|
| 1211 | 2021 Winter |
| 1215 | 2021 Spring |
| 1219 | 2021 Fall |
| 1221 | 2022 Winter |
| 1225 | 2022 Spring |
| 1229 | 2022 Fall |
| 1231 | 2023 Winter |
| 1235 | 2023 Spring |
| 1239 | 2023 Fall |
| 1241 | 2024 Winter |
| 1245 | 2024 Spring |
| 1249 | 2024 Fall |
| 1251 | 2025 Winter |
| 1255 | 2025 Spring |
| 1259 | 2025 Fall |

