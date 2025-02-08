from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
import json
import aitestOrm
from database_connect import get_session

# 读取配置文件
with open('config.json', 'r') as config_file:
	config = json.load(config_file)

# 获取数据库连接
session = get_session('database_aitest')

# 同步所有要测试的模型
def add_models():
	models = config['models']
	for model in models:
		if session.query(aitestOrm.ModelScore).filter(aitestOrm.ModelScore.model_name == model['name']).first() is None:
			session.add(aitestOrm.ModelScore(model_name=model['name']))
			session.commit()
			print(f"Add a new model {model['name']} to database.")

	models_in_db = session.query(aitestOrm.ModelScore).all()
	models_name = [model['name'] for model in models]
	for model in models_in_db:
		if model.model_name not in models_name:
			print(f"{model.model_name} 不在配置文件中，是否删除？(y/n)")
			if input() == 'y':
				session.query(aitestOrm.ModelScore).filter(aitestOrm.ModelScore.model_name == model.model_name).delete()
				session.commit()
				print(f"Delete model {model.model_name} from database.")
			else:
				exit(0)


# 拼接prompt
def splicing_annotation_gen_prompt(model, problem_description, code):
    prompt = {
        "model": model,
        "messages": [
            {"role": "system", "content": f"""你是一个帮助C语言初学者编程的人工智能助手。接下来你会被提供以下内容：
	(1)problem:C语言编程题目描述;
	(2)code:题目对应的C代码。
	你的任务是为编程题目的一份代码生成代码
	注释。"""},
            {"role": "user", "content": f"""
	这是我提供的内容：
	problem:
	{problem_description}
	code:
	{code}"""}
        ],
		"response_format": {"type": "text"},
		"temperature": 0.75
    }
    return json.dumps(prompt, ensure_ascii=False)

def splicing_knlg_exp_prompt(model, knowledge):
	prompt = {
		"model": model,
		"messages": [
			{"role": "system", "content": f"""你是一个帮助C语言初学者编程的人工智能
	助手。接下来你会被提供以下内容：
	(1)knowledge:C语言语法点。
	你的任务是为该语法点生成案例解释。"""},
			{"role": "user", "content": f"""这是我提供的内容：
	knowledge:
	{knowledge}"""}
		],
		"response_format": {"type": "text"},
		"temperature": 0.75
	}
	return json.dumps(prompt, ensure_ascii=False)

def splicing_case_gen_prompt(model, problem_description):
	json_schema = {
		"comment": "以下是我生成的测试样例，测试了xx边界情况...",
		"test_case": [
			{
				"input": "1 2 3\n",
				"output": "3\n2\n1\n"
			},
			{
				"input": "3 2 1\n",
				"output": "1\n2\n3\n"
			}
		]
	}

	prompt = {
		"model": model,
		"messages": [
			{"role": "system", "content": f"""你是一个帮助C语言初学者编程的人工智能助手。接下来你会被提供以下内容：
	(1)problem:C语言编程题目描述。
	你的任务是为该题目生成一些测试样例。请严格按照下面给定的json格式输出：
	{json.dumps(json_schema, ensure_ascii=False)}
	"""},
			{"role": "user", "content": f"""这是我提供的内容：problem:
	{problem_description}"""}
		],
		"response_format": {"type": "json_object"},
		"temperature": 0.75
	}
	return json.dumps(prompt, ensure_ascii=False)

def splicing_code_gen_prompt(model, problem_description):
	json_schema = {
		"comment": "以下是我生成的代码，使用xx算法...",
		"code": "code"
	}

	prompt = {
		"model": model,
		"messages": [
			{"role": "system", "content": f"""你是一个帮助C语言初学者编程的人工智能
	助手。接下来你会被提供以下内容：
	(1)problem:C语言编程题目描述。
	你的任务是为该题目生成一份完整的正确代
	码。
	请严格按照下面给定的json格式输出：
	{json.dumps(json_schema, ensure_ascii=False)}"""},
			{"role": "user", "content": f"""这是我提供的内容：
	problem:
	{problem_description}"""}
		],
		"response_format": {"type": "json_object"},
		"temperature": 0.75
	}
	return json.dumps(prompt, ensure_ascii=False)

def splicing_code_cor_prompt(model, problem_description, code):
	json_schema = {
		"comment": "以下是我纠错后的代码，修改了...",
		"code": "code"
	}

	prompt = {
		"model": model,
		"messages": [
			{"role": "system", "content": f"""你是一个帮助C语言初学者编程的人工智能助手。接下来你会被提供以下内容：(1)problem:C语言编程题目描述;
	(2)code:题目对应一份错误的C代码。你的任务是修改这份错误的代码使得其正确。
	请严格按照下面给定的json格式输出：
	{json.dumps(json_schema, ensure_ascii=False)}"""},
			{"role": "user", "content": f"""这是我提供的内容：problem:
	{problem_description}
	code:
	{code}"""}
		],
		"response_format": {"type": "json_object"},
		"temperature": 0.75
	}
	return json.dumps(prompt, ensure_ascii=False)


# 生成prompt
def generate_annotation_gen_prompt():
	models = session.query(aitestOrm.ModelScore).all()
	codes = session.query(aitestOrm.Code).filter(aitestOrm.Code.accepted <= 1).all()
	cnt = 0
	for model in models:
		for code in codes:
			if session.query(aitestOrm.AnnotationGen).\
				filter(aitestOrm.AnnotationGen.model_name == model.model_name).\
					filter(aitestOrm.AnnotationGen.code_id == code.code_id).first() is None:
				anno_gen = aitestOrm.AnnotationGen(
					model_name=model.model_name,
					code_id=code.code_id,
				)
				session.add(anno_gen)
				session.flush()

				cnt += 1

				code_str = code.code
				problem = code.problem_for_code
				problem_str = problem.full_description()

				json_str = splicing_annotation_gen_prompt(model.model_name, problem_str, code_str)

				prompt = aitestOrm.PromptComp(
					prompt_json=json_str,
					type=1,
					sc_id=anno_gen.sc_id
				)
				session.add(prompt)

	session.commit()
	print(f"insert {cnt} annotation_gen prompts.")

def generate_knlg_exp_prompt():
	models = session.query(aitestOrm.ModelScore).all()
	knwoledges = session.query(aitestOrm.KnowledgePoint).all()
	cnt = 0
	for model in models:
		for knlg in knwoledges:
			if session.query(aitestOrm.KnlgExp).\
				filter(aitestOrm.KnlgExp.model_name == model.model_name).\
					filter(aitestOrm.KnlgExp.knlg_id == knlg.knlg_id).first() is None:
				knlg_exp = aitestOrm.KnlgExp(
					model_name=model.model_name,
					knlg_id=knlg.knlg_id,
				)
				session.add(knlg_exp)
				session.flush()

				cnt += 1

				knlg_str = knlg.content
				json_str = splicing_knlg_exp_prompt(model.model_name, knlg_str)

				prompt = aitestOrm.PromptComp(
					prompt_json=json_str,
					type=2,
					sc_id=knlg_exp.sc_id
				)
				session.add(prompt)

	session.commit()
	print(f"insert {cnt} knowledge_exp prompts.")

def generate_case_gen_prompt():
	models = session.query(aitestOrm.ModelScore).all()
	problems = session.query(aitestOrm.Problem).all()
	cnt = 0
	for model in models:
		for problem in problems:
			if session.query(aitestOrm.CaseGen).\
				filter(aitestOrm.CaseGen.model_name == model.model_name).\
					filter(aitestOrm.CaseGen.problem_id == problem.problem_id).first() is None:
				case_gen = aitestOrm.CaseGen(
					model_name=model.model_name,
					problem_id=problem.problem_id,
				)
				session.add(case_gen)
				session.flush()

				cnt += 1

				problem_str = problem.full_description()

				json_str = splicing_case_gen_prompt(model.model_name, problem_str)

				prompt = aitestOrm.PromptComp(
					prompt_json=json_str,
					type=3,
					sc_id=case_gen.sc_id
				)
				session.add(prompt)

	session.commit()
	print(f"insert {cnt} case_gen prompts.")

def generate_code_gen_prompt():
	models = session.query(aitestOrm.ModelScore).all()
	problems = session.query(aitestOrm.Problem).all()
	cnt = 0
	for model in models:
		for problem in problems:
			if session.query(aitestOrm.CodeGen).\
				filter(aitestOrm.CodeGen.model_name == model.model_name).\
					filter(aitestOrm.CodeGen.problem_id == problem.problem_id).first() is None:
				code_gen = aitestOrm.CodeGen(
					model_name=model.model_name,
					problem_id=problem.problem_id,
				)
				session.add(code_gen)
				session.flush()

				cnt += 1

				problem_str = problem.full_description()

				json_str = splicing_code_gen_prompt(model.model_name, problem_str)

				prompt = aitestOrm.PromptComp(
					prompt_json=json_str,
					type=4,
					sc_id=code_gen.sc_id
				)
				session.add(prompt)

	session.commit()
	print(f"insert {cnt} code_gen prompts.")

def generate_code_cor_prompt():
	models = session.query(aitestOrm.ModelScore).all()
	codes = session.query(aitestOrm.Code).filter(aitestOrm.Code.accepted == 2).all()
	cnt = 0
	for model in models:
		for code in codes:
			if session.query(aitestOrm.CodeCor).\
				filter(aitestOrm.CodeCor.model_name == model.model_name).\
					filter(aitestOrm.CodeCor.code_id == code.code_id).first() is None:
				code_cor = aitestOrm.CodeCor(
					model_name=model.model_name,
					code_id=code.code_id,
				)
				session.add(code_cor)
				session.flush()

				cnt += 1

				code_str = code.code
				problem = code.problem_for_code
				problem_str = problem.full_description()

				json_str = splicing_code_cor_prompt(model.model_name, problem_str, code_str)

				prompt = aitestOrm.PromptComp(
					prompt_json=json_str,
					type=5,
					sc_id=code_cor.sc_id
				)
				session.add(prompt)

	session.commit()
	print(f"insert {cnt} code_cor prompts.")


def generate_prompt():
	add_models()
	generate_annotation_gen_prompt()
	generate_knlg_exp_prompt()
	generate_case_gen_prompt()
	generate_code_gen_prompt()
	generate_code_cor_prompt()
	print("generate prompt Done!")

if __name__ == '__main__':
	add_models()			
	generate_annotation_gen_prompt()
	generate_knlg_exp_prompt()
	generate_case_gen_prompt()
	generate_code_gen_prompt()
	generate_code_cor_prompt()


	print("generate prompt Done!")