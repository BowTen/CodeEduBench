import json
from sqlalchemy import create_engine, func, text, insert
from sqlalchemy.orm import sessionmaker
import jolOrm
import aitestOrm
from database_connect import get_session
from truncateTable import truncate_all


# 读取配置文件
with open('config.json', 'r') as config_file:
	config = json.load(config_file)


# 获取题目难度区间
problem_interval = config['problem_interval']
easy = problem_interval['easy']
medium = problem_interval['medium']
hard = problem_interval['hard']

# 获取代码数量
code_num = config['code_num']
easy_code = code_num['easy']
medium_code = code_num['medium']
hard_code = code_num['hard']

wa_code_num = config['wa_code_num']
wa_easy_code = wa_code_num['easy']
wa_medium_code = wa_code_num['medium']
wa_hard_code = wa_code_num['hard']

# 获取题目数量
problem_num = config['problem_num']
easy_problem = problem_num['easy']
medium_problem = problem_num['medium']
hard_problem = problem_num['hard']

# 获取数据库连接
session = get_session('database')
aisession = get_session('database_aitest')



def get_solutions(wa, L, R, num):
	query = session.query(jolOrm.Solution)
	if wa == 1:
		query = query.filter(jolOrm.Solution.result != 4)
	solutions = query.\
		filter(jolOrm.Solution.language == 0).\
		join(jolOrm.Problem, jolOrm.Problem.problem_id == jolOrm.Solution.problem_id).\
		filter(jolOrm.Problem.spj == 0).\
		filter(jolOrm.Problem.accepted >= L * jolOrm.Problem.submit).\
		filter(jolOrm.Problem.score < R * jolOrm.Problem.submit).\
		order_by(func.random()).\
		limit(num).all()
	return solutions

def get_problems(L, R, num):
	problems = session.query(jolOrm.Problem).\
		filter(jolOrm.Problem.solved_user > 0).\
		filter(jolOrm.Problem.spj == 0).\
		filter(jolOrm.Problem.score >= L * jolOrm.Problem.submit).\
		filter(jolOrm.Problem.score < R * jolOrm.Problem.submit).\
		filter(jolOrm.Problem.sample_input != None).\
		order_by(func.random()).\
		limit(num).all()
	return problems

def insert_solutions(solutions, cor = 0):
	for solution in solutions:
		problem = aitestOrm.ProblemForCode(solution.problem)
		code = aitestOrm.Code(
			problem_id=problem.problem_id,
			code=solution.source_code.source,
			accepted=(solution.result==4)
		)
		if cor == 1:
			code.accepted = 2
		if aisession.query(aitestOrm.ProblemForCode).filter(aitestOrm.ProblemForCode.problem_id==problem.problem_id).first() is None:
			aisession.add(problem)
		aisession.add(code)
	aisession.commit()

def insert_problems(problems):
	for jol_problem in problems:
		problem = aitestOrm.Problem(jol_problem)
		if aisession.query(aitestOrm.Problem).filter(aitestOrm.Problem.problem_id==problem.problem_id).first() is None:
			aisession.add(problem)
	aisession.commit()

def extract_code():

	aisession.query(aitestOrm.Code).delete()
	aisession.query(aitestOrm.ProblemForCode).delete()

	easy_solutions = get_solutions(0, 0, hard, hard_code)
	medium_solutions = get_solutions(0, hard, medium, medium_code)
	hard_solutions = get_solutions(0, medium, easy, easy_code)
	insert_solutions(easy_solutions)
	print(f"insert {len(easy_solutions)} easy codes.")
	insert_solutions(medium_solutions)
	print(f"insert {len(medium_solutions)} medium codes.")
	insert_solutions(hard_solutions)
	print(f"insert {len(hard_solutions)} hard codes.")


	easy_solutions = get_solutions(1, 0, hard, wa_hard_code)
	medium_solutions = get_solutions(1, hard, medium, wa_medium_code)
	hard_solutions = get_solutions(1, medium, easy, wa_easy_code)
	insert_solutions(easy_solutions, 1)
	print(f"insert {len(easy_solutions)} easy wrong codes.")
	insert_solutions(medium_solutions, 1)
	print(f"insert {len(medium_solutions)} medium wrong codes.")
	insert_solutions(hard_solutions, 1)
	print(f"insert {len(hard_solutions)} hard wrong codes.")

def extract_problem():

	aisession.query(aitestOrm.Problem).delete()

	easy_problems = get_problems(0, hard, hard_problem)
	medium_problems = get_problems(hard, medium, medium_problem)
	hard_problems = get_problems(medium, easy, easy_problem)
	insert_problems(easy_problems)
	print(f"insert {len(easy_problems)} easy problems.")
	insert_problems(medium_problems)
	print(f"insert {len(medium_problems)} medium problems.")
	insert_problems(hard_problems)
	print(f"insert {len(hard_problems)} hard problems.")

def insert_knowledge_point():
	data = [
    	{"content": "#include 预处理指令", "level": 1},
    	{"content": "main() 函数", "level": 1},
    	{"content": "注释 (// 单行注释, /* ... */ 多行注释)", "level": 1},
    	{"content": "基本数据类型int", "level": 1},
    	{"content": "基本数据类型float", "level": 1},
    	{"content": "基本数据类型double", "level": 1},
    	{"content": "基本数据类型char", "level": 1},
    	{"content": "修饰符short", "level": 1},
    	{"content": "修饰符long", "level": 1},
    	{"content": "修饰符signed", "level": 1},
    	{"content": "修饰符unsigned", "level": 1},
    	{"content": "基本输入 scanf()", "level": 1},
    	{"content": "基本输出 printf()", "level": 1},
    	{"content": "类型定义typedef", "level": 1},
    	{"content": "变量声明和初始化", "level": 1},
    	{"content": "常量中的const 关键字", "level": 1},
    	{"content": "#define 宏定义", "level": 1},
    	{"content": "#undef 取消宏定义", "level": 1},
    	{"content": "算术运算符 +", "level": 1},
    	{"content": "算术运算符 -", "level": 1},
    	{"content": "算术运算符 *", "level": 1},
    	{"content": "算术运算符 /", "level": 1},
    	{"content": "算术运算符 %", "level": 1},
    	{"content": "关系运算符中的 ==", "level": 1},
    	{"content": "关系运算符中的 !=", "level": 1},
    	{"content": "关系运算符中的 >", "level": 1},
    	{"content": "关系运算符中的 <", "level": 1},
    	{"content": "关系运算符中的 >=", "level": 1},
    	{"content": "关系运算符中的 <=", "level": 1},
    	{"content": "逻辑运算符中的 &&", "level": 1},
    	{"content": "逻辑运算符中的 ||", "level": 1},
    	{"content": "逻辑运算符中的 !", "level": 1},
    	{"content": "位运算符中的 &", "level": 1},
    	{"content": "位运算符中的 |", "level": 1},
    	{"content": "位运算符中的 ^", "level": 1},
    	{"content": "位运算符中的 ~", "level": 1},
    	{"content": "位运算符中的 <<", "level": 1},
    	{"content": "位运算符中的 >>", "level": 1},
    	{"content": "赋值运算符 =", "level": 1},
    	{"content": "赋值运算符+=", "level": 1},
    	{"content": "赋值运算符-=", "level": 1},
    	{"content": "赋值运算符*=", "level": 1},
    	{"content": "赋值运算符/=", "level": 1},
    	{"content": "赋值运算符%=", "level": 1},
    	{"content": "sizeof运算符", "level": 1},
    	{"content": "& (取地址运算符)", "level": 1},
    	{"content": "* (指针运算符)", "level": 1},
    	{"content": "条件运算符：? :", "level": 1},
    	{"content": "转义字符\\n", "level": 1},
    	{"content": "转义字符\\t", "level": 1},
    	{"content": "选择结构中的if", "level": 1},
    	{"content": "选择结构中的if-else", "level": 1},
    	{"content": "选择结构中的switch", "level": 1},
    	{"content": "条件语句中的case", "level": 1},
    	{"content": "条件语句中的default", "level": 1},
    	{"content": "循环语句中的for", "level": 1},
    	{"content": "循环语句中的while", "level": 1},
    	{"content": "循环语句中的do-while", "level": 1},
    	{"content": "跳转语句中的break", "level": 1},
    	{"content": "跳转语句中的continue", "level": 1},
    	{"content": "跳转语句中的return", "level": 1},
    	{"content": "跳转语句中的goto", "level": 1},
    	{"content": "指针的基本概念", "level": 2},
    	{"content": "指针的声明和初始化", "level": 2},
    	{"content": "指针的算术运算", "level": 2},
    	{"content": "指针数组", "level": 2},
    	{"content": "数组指针", "level": 2},
    	{"content": "函数指针", "level": 2},
    	{"content": "多级指针", "level": 2},
    	{"content": "指针与字符串", "level": 2},
    	{"content": "指针的类型转换", "level": 2},
    	{"content": "动态内存管理中的malloc", "level": 2},
    	{"content": "动态内存管理中的calloc", "level": 2},
    	{"content": "动态内存管理中的realloc", "level": 2},
    	{"content": "动态内存管理中的free", "level": 2},
    	{"content": "文件指针 FILE", "level": 2},
    	{"content": "文件打开 fopen", "level": 2},
    	{"content": "文件关闭 fclose", "level": 2},
    	{"content": "文件读写 fprintf", "level": 2},
    	{"content": "文件读写 fscanf", "level": 2},
    	{"content": "文件读写 fgets", "level": 2},
    	{"content": "文件读写 fputs", "level": 2},
    	{"content": "文件读写 fgetc", "level": 2},
    	{"content": "文件读写 fputc", "level": 2},
    	{"content": "文件读写 fread", "level": 2},
    	{"content": "文件读写 fwrite", "level": 2},
    	{"content": "文件定位 fseek", "level": 2},
    	{"content": "文件定位 ftell", "level": 2},
    	{"content": "文件定位 rewind", "level": 2},
    	{"content": "内存分区中的栈区", "level": 2},
    	{"content": "内存分区中的堆区", "level": 2},
    	{"content": "内存分区中的全局区", "level": 2},
    	{"content": "内存分区中的常量区", "level": 2},
    	{"content": "内存分区中的代码区", "level": 2}
	]

	data = [
	    {"content": "#include 预处理指令", "level": 1},
	    {"content": "main() 函数", "level": 1},
	    {"content": "结构体成员的访问", "level": 1},
	    {"content": "指针的基本概念", "level": 2},
	    {"content": "内存分区中的代码区", "level": 2}
	]

	aisession.execute(insert(aitestOrm.KnowledgePoint), data)
	aisession.commit()
	num = aisession.query(aitestOrm.KnowledgePoint).count()
	print(f"insert {num} knowledge points.")

def extract_data():
	truncate_all()
	extract_code()
	extract_problem()
	insert_knowledge_point()

if __name__ == '__main__':
	#extract_code()
	#extract_problem()
	extract_data()
	print("over!")