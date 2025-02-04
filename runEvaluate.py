from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
from openai import OpenAI
import json
import aitestOrm
from database_connect import get_session
import time
import requests

# 读取配置文件
with open('config.json', 'r') as config_file:
	config = json.load(config_file)

# 获取数据库连接
session = get_session('database_aitest')

# 创建openai客户端
eval_model = config['evaluate_model']['name']
eval_api_key = config['evaluate_model']['api_key']
eval_base_url = config['evaluate_model']['base_url']

client = OpenAI(
	api_key = eval_api_key,
	base_url = eval_base_url
)

table = [aitestOrm.AnnotationGen, aitestOrm.KnlgExp, aitestOrm.CaseGen, aitestOrm.CodeGen, aitestOrm.CodeCor]

def run_evaluate_by_prompt(prompt):
	if prompt.eval_id != None:
		print(f"Evaluate {prompt.prompt_id} has been solved.")
		return 0
	
	params = json.loads(prompt.prompt_json)


	#response = client.chat.completions.create(**params)
	response = None

	# 最大重试次数
	max_retries = 5
	wait_time = 20
	retry_count = 0
	success = False

	while retry_count < max_retries and not success:
		try:
			# 发起请求，并设置超时为15秒
			response = client.chat.completions.create(**params, timeout=wait_time)
			success = True  # 请求成功
		except requests.exceptions.Timeout:
			retry_count += 1
			wait_time += 10
			print(f"请求超时，第{retry_count}次重试...")
			time.sleep(2)  # 等待2秒再重试
		except Exception as e:
			print(f"发生错误: {e}")
			exit(0)  # 发生其他错误时停止重试

	if response is None:
		print(f"Prompt {prompt.prompt_id} complement failed.")
		return 0





	content = response.choices[0].message.content
	evaluate_gen = aitestOrm.EvaluateGen(content=content)
	session.add(evaluate_gen)
	session.flush()
	prompt.eval_id = evaluate_gen.eval_id

	content = json.loads(response.choices[0].message.content)

	prompt_type = '[type]'
	if prompt.type == 1:
		prompt_type = 'AnnotationGen'
		score = session.query(aitestOrm.AnnotationGen).filter(aitestOrm.AnnotationGen.sc_id == prompt.sc_id).first()
		score.accuracy = content['accuracy']
		score.simplicity = content['simplicity']
		score.naturalness = content['naturalness']
		score.usefulness = content['usefulness']
	elif prompt.type == 2:
		prompt_type = 'KnlgExp'
		score = session.query(aitestOrm.KnlgExp).filter(aitestOrm.KnlgExp.sc_id == prompt.sc_id).first()
		score.accuracy = content['accuracy']
		score.correlation = content['correlation']
		score.understandability = content['understandability']
	elif prompt.type == 3:
		prompt_type = 'CaseGen'
		score = session.query(aitestOrm.CaseGen).filter(aitestOrm.CaseGen.sc_id == prompt.sc_id).first()
		score.comprehensive = content['comprehensive']
	elif prompt.type == 4:
		prompt_type = 'CodeGen'
		score = session.query(aitestOrm.CodeGen).filter(aitestOrm.CodeGen.sc_id == prompt.sc_id).first()
		score.readability = content['readability']
		score.performance = content['performance']
	elif prompt.type == 5:
		prompt_type = 'CodeCor'
		score = session.query(aitestOrm.CodeCor).filter(aitestOrm.CodeCor.sc_id == prompt.sc_id).first()
		score.understandability = content['understandability']

	session.commit()
	print(f"Generate evaluate for {prompt_type} prompt {prompt.prompt_id} successfully. eval_id: {evaluate_gen.eval_id}")
	return 1

#run_evaluate_by_prompt(prompt)


def run_evaluate():
	invalid_prompts = 0
	prompts_num = 0
	prompts = session.query(aitestOrm.PromptEval).all()
	for prompt in prompts:
		score_table = table[prompt.type - 1]
		score = session.query(score_table).filter(score_table.sc_id == prompt.sc_id).first()
		if score is None:
			session.query(aitestOrm.EvaluateGen).filter(aitestOrm.EvaluateGen.eval_id == prompt.eval_id).delete()
			session.delete(prompt)
			session.commit()
			invalid_prompts += 1
			continue

		if prompt.eval_id != None:
			continue	
		prompts_num += run_evaluate_by_prompt(prompt)

		# 为了防止请求过快而超过token限制，每次请求后等待0.2秒
		time.sleep(0.2)

	print(f"Invalid prompts: {invalid_prompts} is deleted.")
	print(f"Generate evaluate for {prompts_num} prompts successfully.")


if __name__ == '__main__':
	run_evaluate()