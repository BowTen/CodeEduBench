import json
from sqlalchemy import create_engine, func, text
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

# 获取题目数量
problem_num = config['problem_num']
easy_problem = problem_num['easy']
medium_problem = problem_num['medium']
hard_problem = problem_num['hard']

# 获取数据库连接
session = get_session('database')
aisession = get_session('database_aitest')



def get_solutions(ac, L, R, num):
	query = session.query(jolOrm.Solution)
	if ac == 1:
		query = query.filter(jolOrm.Solution.result == 4)
	else:
		query = query.filter(jolOrm.Solution.result != 4)
	solutions = query.\
		filter(jolOrm.Solution.language == 0).\
		join(jolOrm.Problem, jolOrm.Problem.problem_id == jolOrm.Solution.problem_id).\
		filter(jolOrm.Problem.spj == 0).\
		filter(jolOrm.Problem.score > L).\
		filter(jolOrm.Problem.score <= R).\
		order_by(func.random()).\
		limit(num).all()
	return solutions

def get_problems(L, R, num):
	problems = session.query(jolOrm.Problem).\
		filter(jolOrm.Problem.solved_user > 0).\
		filter(jolOrm.Problem.spj == 0).\
		filter(jolOrm.Problem.score > L).\
		filter(jolOrm.Problem.score <= R).\
		filter(jolOrm.Problem.sample_input != None).\
		order_by(func.random()).\
		limit(num).all()
	return problems

def insert_solutions(solutions):
	for solution in solutions:
		problem = aitestOrm.ProblemForCode(solution.problem)
		code = aitestOrm.Code(
			problem_id=problem.problem_id,
			code=solution.source_code.source,
			accepted=(solution.result==4)
		)
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

	easy_solutions = get_solutions(1, 0, easy, easy_code)
	medium_solutions = get_solutions(1, easy, medium, medium_code)
	hard_solutions = get_solutions(1, medium, hard, hard_code)
	insert_solutions(easy_solutions)
	print(f"insert {len(easy_solutions)} easy codes.")
	insert_solutions(medium_solutions)
	print(f"insert {len(medium_solutions)} medium codes.")
	insert_solutions(hard_solutions)
	print(f"insert {len(hard_solutions)} hard codes.")


	easy_solutions = get_solutions(0, 0, easy, easy_code)
	medium_solutions = get_solutions(0, easy, medium, medium_code)
	hard_solutions = get_solutions(0, medium, hard, hard_code)
	insert_solutions(easy_solutions)
	insert_solutions(medium_solutions)
	insert_solutions(hard_solutions)

def extract_problem():

	aisession.query(aitestOrm.Problem).delete()

	easy_problems = get_problems(0, easy, easy_problem)
	medium_problems = get_problems(easy, medium, medium_problem)
	hard_problems = get_problems(medium, hard, hard_problem)
	insert_problems(easy_problems)
	print(f"insert {len(easy_problems)} easy problems.")
	insert_problems(medium_problems)
	print(f"insert {len(medium_problems)} medium problems.")
	insert_problems(hard_problems)
	print(f"insert {len(hard_problems)} hard problems.")

def extract_data():
	truncate_all()
	extract_code()
	extract_problem()

if __name__ == '__main__':
	extract_code()
	extract_problem()
	print("over!")