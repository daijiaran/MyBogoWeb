import json
import re
from datetime import datetime

def parse_judge_questions(text):
    """解析判断题"""
    judge_questions = []
    
    # 提取判断题部分
    judge_section = re.search(r'第一题：判断对错(.*?)第二题：选择题', text, re.DOTALL)
    if judge_section:
        judge_text = judge_section.group(1)
        
        # 匹配所有判断题
        pattern = r'[\(（](\d+)[\)）]\s+(.*?)\n([√×])'
        matches = re.findall(pattern, judge_text, re.DOTALL)
        
        for i, (num, content, answer) in enumerate(matches):
            question = {
                "id": i,
                "type": "single",
                "content": f"\n          <p><span>{num}.</span>&nbsp; <span>{content.strip()}</span></p>\n        ",
                "options": [
                    {"label": "正确(True)", "html": "正确(True)"},
                    {"label": "错误(False)", "html": "错误(False)"}
                ],
                "correctAnswer": "正确(True)" if answer == "√" else "错误(False)",
                "userAnswer": "",
                "explanation": "",
                "meta": f"\n          {num}、判断题（1分）\n          分值：1分\n          难度：适中\n        "
            }
            judge_questions.append(question)
    
    return judge_questions

def parse_single_questions(text):
    """解析单选题"""
    single_questions = []
    
    # 提取选择题部分
    single_section = re.search(r'第二题：选择题(.*?)', text, re.DOTALL)
    if not single_section:
        return single_questions
        
    single_text = single_section.group(1)
    
    # 手动定义题目和答案
    # 从temp.txt中手动提取题目
    questions_data = [
        # （1）到（10）
        {"num": 1, "content": "数据库管理系统(DBMS)  是(    )。", "options": ["一个完整的数据库应用系统", "一组硬件", "一组软件", "既有硬件，也有软件"], "answer": "C"},
        {"num": 2, "content": "用户或应用程序看到的那部分局部逻辑结构和特征的描述是 (    )模式。", "options": ["模式", "物理模式", "子模式", "内模式"], "answer": "C"},
        {"num": 3, "content": "数据库(DB),    数据库系统(DBS)  和数据库管理系统(DBMS)之间的关系是(       )。", "options": ["DBS包括DB和DBMS", "DBMS包括DB和DBS", "DB包括DBS和DBMS", "DBS就是DB,  也就是DBMS"], "answer": "A"},
        {"num": 4, "content": "数据库的概念模型独立于(       )。", "options": ["具体的机器和DBMS", "E-R图", "信息世界", "现实世界"], "answer": "A"},
        {"num": 5, "content": "在关系R( R#, RN, S# )和 S( S#,SN, SD )中,R的主码是R#, S的主码是S#,则S#在R中称为 (     )。", "options": ["外码", "候选码", "主码", "超码"], "answer": "A"},
        {"num": 6, "content": "采用SQL查询语言对关系进行查询操作,若要求查询结果中不能出现重复元组,可在 SELECT子句后增加保留字(     )。", "options": ["DISTINCT", "UNIQUE", "NOT NULL", "SINGLE"], "answer": "A"},
        {"num": 7, "content": "数据库管理系统能实现对数据库中数据的查询、插入、修改和删除,这类功能称为(     )。", "options": ["数据定义功能", "数据管理功能", "数据操纵功能", "数据控制功能"], "answer": "C"},
        {"num": 8, "content": "关系模型中,一个码是(   )。", "options": ["可由多个任意属性组成", "至多由一个属性组成", "可由一个或多个其值能唯一标识该关系模式中任何元组的最少属性组成", "以上都不是"], "answer": "C"},
        {"num": 9, "content": "在SQL语句中, 需要对分组情况应满足的条件进行判断时,应使用(     )。", "options": ["GROUP BY", "ORDER BY", "WHERE", "HAVING"], "answer": "D"},
        {"num": 10, "content": "SQL语言是(     )。", "options": ["高级语言", "结构化查询语言", "编程语言", "宿主语言"], "answer": "B"},
        {"num": 11, "content": "数据库三级模式,反映了三种不同角度看待数据库的观点,用户眼中的数据库称为(     )。", "options": ["存储模式", "概念模式", "内模式", "外模式"], "answer": "D"},
        # （12）到（20）
        {"num": 12, "content": "在数据库设计中, E-R图产生于(     )。", "options": ["需求分析阶段", "物理设计阶段", "逻辑设计阶段", "概念设计阶段"], "answer": "D"},
        {"num": 13, "content": "有一个关系:学生(学号,姓名,系别),规定学号的值域是8个数字组成的字符串,这一规则属于(     )。", "options": ["实体完整性约束", "参照完整性约束", "用户自定义完整性约束", "关键字完整性约束"], "answer": "C"},
        {"num": 14, "content": "关系模型是(     )。", "options": ["用关系表示实体", "用关系表示联系", "用关系表示实体及其联系", "用关系表示属性"], "answer": "C"},
        {"num": 15, "content": "概念模型是现实世界的第一层抽象，这一类模型中最著名的模型是（ ）。", "options": ["层次模型", "关系模型", "网状模型", "实体-联系模型"], "answer": "D"},
        {"num": 16, "content": "设有关系B（书号，书名），如果要检索第3个字母为N ，且至少包含4个字母的书名，则SQL查询语句中WHERE子句的条件表达式应写成：书名 Like（   ）。", "options": ["'    N _ '", "'    N% '", "'    N _ % '", "'_%N      '"], "answer": "C"},
        {"num": 17, "content": "设一个实验项目可以有多名同学参加，每名同学可参加多个实验项目，那么学生与实验项目之间是(     )。", "options": ["一对一的关系", "一对多的关系", "多对一的关系", "多对多的关系"], "answer": "D"},
        {"num": 18, "content": "采用二维表格结构表达实体型及实体间联系的数据模型是(     )。", "options": ["层次模型", "网状模型", "关系模型", "实体联系模型"], "answer": "C"},
        {"num": 19, "content": "现实世界中的事物个体在信息世界中称为(     )。", "options": ["实体", "实体集", "字段", "记录"], "answer": "A"},
        {"num": 20, "content": "实体完整性和参照完整性是关系模型必须满足的完整性约束条件，并称为关系的两个不变性，应该有关系系统自动支持；(    )是应用领域需要遵循的约束条件，体现了具体领域的语义约束", "options": ["实体完整性", "参照完整性", "用户定义的完整性", "用户安全性"], "answer": "C"},
        # （21）到（30）
        {"num": 21, "content": "下列实体类型的联系中，属于多对多联系的是() A、 学校与教师之间的联系", "options": ["学校与教师之间的联系", "学生与课程之间的联系", "商品条形码与商品之间的联系", "班级与班长之间的联系"], "answer": "B"},
        {"num": 22, "content": "下面的选项不是关系数据库基本特征的是（  ）。", "options": ["不同的列应有不同的数据类型", "不同的列应有不同的列名", "与行的次序无关", "与列的次序无关"], "answer": "A"},
        {"num": 23, "content": "在关系模式R(U)中，X ≤ U, Y ≤ U, X→Y，且Y不能决定X，则Y与X之间的关系是", "options": ["一对一", "一对多", "多对多", "多对一"], "answer": "B"},
        {"num": 24, "content": "规范化理论是数据库设计的重要依据，其主要目标是什么？", "options": ["增加数据冗余", "降低数据一致性", "提高数据存储效率", "消除数据冗余，确保数据一致性和完整性"], "answer": "D"},
        {"num": 25, "content": "规范化理论是数据库设计的重要依据，其主要目标是什么？", "options": ["增加数据冗余", "降低数据一致性", "提高数据存储效率", "消除数据冗余，确保数据一致性和完整性"], "answer": "D"},
        {"num": 26, "content": "满足第二范式（2NF）的关系模式，必须满足什么条件？", "options": ["所有属性都是不可再分的原子值", "每个非主属性都完全依赖于整个主键", "消除了部分函数依赖", "所有非主属性对主键都是传递依赖"], "answer": "C"},
        {"num": 27, "content": "在关系模式R(A, B, C, D)中，若存在函数依赖A→B和B→C，则R最高可以达到哪个范式？", "options": ["1NF", "2NF", "3NF", "BCNF"], "answer": "B"},
        {"num": 28, "content": "事务的四个基本属性（ACID）不包括以下哪一项？", "options": ["原子性（Atomicity）", "完整性（Integrity）", "一致性（Consistency）", "持久性（Durability）"], "answer": "B"},
        {"num": 29, "content": "在并发控制中，为了避免脏读、不可重复读和幻读等问题，通常会使用以下哪种机制 ?", "options": ["封锁机制", "索引机制", "缓存机制", "排序机制"], "answer": "A"},
        {"num": 30, "content": "当事务T获得了数据对象R的X锁控制权时，T对R可以进行以下哪种操作？", "options": ["只可读", "可读也可写", "只可写", "不可读也不可写"], "answer": "B"},
        # （31）到（40）
        {"num": 31, "content": "关系代数中，关系模型基本的数据结构是？", "options": ["树", "图", "索引", "关系"], "answer": "D"},
        {"num": 32, "content": "关系代数中，关系数据库的查询语言通常属于哪种类型？", "options": ["过程性语言", "第三代语言", "非过程性语言", "高级程序设计语言"], "answer": "C"},
        {"num": 33, "content": "在关系模型中，关于实体完整性的描述，正确的是？", "options": ["实体不允许是空实体", "实体的主键值不允许是空值", "实体的外键值不允许是空值", "实体的属性值不允许是空值"], "answer": "B"},
        {"num": 34, "content": "关系代数中，关系数据库的数据操作通常分为哪两类？", "options": ["查询和更新", "排序和索引", "插入和删除", "修改和排序"], "answer": "A"},
        {"num": 35, "content": "数据库的完整性主要关注的是哪一方面？", "options": ["数据的正确性", "数据的存储效率", "数据的传输速度", "数据的显示格式"], "answer": "A"},
        {"num": 36, "content": "以下哪个选项不是数据完整性的组成部分？", "options": ["实体完整性", "参照完整性", "数据加密性", "用户自定义完整性"], "answer": "C"},
        {"num": 37, "content": "数据库完整性检查和控制的主要目的是什么？", "options": ["提高数据存储效率", "加快数据查询速度", "防止不合语义的数据进入数据库", "增加数据的冗余度"], "answer": "C"},
        {"num": 38, "content": "需求分析的主要任务是什么？", "options": ["确定数据存储结构", "确定数据访问方式", "明确用户需求并确定新系统功能", "设计数据库的物理结构"], "answer": "C"},
        {"num": 39, "content": "需求分析阶段，以下哪项不是重点考虑的内容？", "options": ["用户的数据处理需求", "用户的安全性需求", "数据库的物理存储结构", "数据的完整性和一致性需求"], "answer": "C"},
        {"num": 40, "content": "数据库管理系统通常提供哪种功能来控制不同用户访问数据的权限？", "options": ["授权功能", "加密功能", "防火墙功能", "审计功能"], "answer": "A"}
    ]
    
    # 生成单选题
    for i, q_data in enumerate(questions_data):
        question = {
            "id": i,
            "type": "single",
            "content": f"\n          <p>{q_data['content']}</p>\n        ",
            "options": [
                {"label": "A", "html": f"  {q_data['options'][0]}"},
                {"label": "B", "html": f"  {q_data['options'][1]}"},
                {"label": "C", "html": f"  {q_data['options'][2]}"},
                {"label": "D", "html": f"  {q_data['options'][3]}"}
            ],
            "correctAnswer": q_data['answer'],
            "userAnswer": "",
            "explanation": "",
            "meta": f"\n          {q_data['num']}、单选题（1分）\n          分值：1分\n          难度：适中\n        "
        }
        single_questions.append(question)
    
    return single_questions

def main():
    # 读取temp.txt文件
    with open('c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\documents\\temp.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 解析题目
    judge_questions = parse_judge_questions(text)
    single_questions = parse_single_questions(text)
    
    print(f"解析到判断题：{len(judge_questions)}道")
    print(f"解析到单选题：{len(single_questions)}道")
    
    # 生成试卷
    judge_exam = {
        "id": f"{int(datetime.now().timestamp() * 1000)}",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "title": "数据库原理判断题",
        "questions": judge_questions
    }
    
    single_exam = {
        "id": f"{int(datetime.now().timestamp() * 1000) + 1}",
        "timestamp": int(datetime.now().timestamp() * 1000) + 1,
        "title": "数据库原理单选题",
        "questions": single_questions
    }
    
    # 输出到文件
    judge_output_path = 'c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\数据库原理判断题.json'
    single_output_path = 'c:\\Users\\DAI\\IdeaProjects\\vue_project_2\\.trae\\数据库原理单选题.json'
    
    with open(judge_output_path, 'w', encoding='utf-8') as f:
        json.dump(judge_exam, f, ensure_ascii=False, indent=2)
    
    with open(single_output_path, 'w', encoding='utf-8') as f:
        json.dump(single_exam, f, ensure_ascii=False, indent=2)
    
    print(f"\n判断题输出到：{judge_output_path}")
    print(f"单选题输出到：{single_output_path}")

if __name__ == "__main__":
    main()
