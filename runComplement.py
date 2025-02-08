import aitestOrm
import database_connect
import json
import time
import requests
from apiCalls import call, ollama_run, ollama_stop, get_model_config
from jsonschema import validate, ValidationError
from vllm import LLM, SamplingParams
from time import sleep
import subprocess
import sys
import signal

son_process = None

# 定义信号处理函数
def handle_signal(signum, frame):
	global son_process
	if son_process is not None:
		print(f"收到信号 {signum}，终止子进程...")
		son_process.terminate()  # 发送 SIGTERM 给子进程
	exit(0)

# 注册信号处理
signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

def get_json(s):
	while len(s) > 0 and s[0] != '{':
		s = s[1:]
	while len(s) > 0 and s[-1] != '}':
		s = s[:-1]
	return s


# 读取配置文件
with open('config.json', 'r') as config_file:
	config = json.load(config_file)

# 获取数据库连接
session = database_connect.get_session('database_aitest')

tables = [aitestOrm.AnnotationGen, aitestOrm.KnlgExp, aitestOrm.CaseGen, aitestOrm.CodeGen, aitestOrm.CodeCor]

schemas = [
	{
		"type": "object",
		"properties": {
			"comment": {"type": "string"},
			"test_case": {
				"type": "array",
				"items": {
					"type": "object",
					"properties": {
						"input": {"type": "string"},
						"output": {"type": "string"}
					},
					"required": ["input", "output"],
					"additionalProperties": False
				}
			}
		},
		"required": ["comment", "test_case"],  # 必填字段
		"additionalProperties": False  # 不允许额外的属性
	},
	{
		"type": "object",
		"properties": {
			"comment": {"type": "string"},
			"code": {"type": "string"}
		},
		"required": ["comment", "code"],  # 必填字段
		"additionalProperties": False  # 不允许额外的属性
	},
	{
		"type": "object",
		"properties": {
			"comment": {"type": "string"},
			"code": {"type": "string"}
		},
		"required": ["comment", "code"],  # 必填字段
		"additionalProperties": False  # 不允许额外的属性
	}
]

default_complement = [
	{
		"comment": "测试样例生成失败",
		"test_case": [
			{
				"input": "#@%",
				"output": "*&^"
			}
		]
	},
	{
		"comment": "代码生成失败",
		"code": "#@%"
	},
	{
		"comment": "代码纠错失败",
		"code": "#@%"
	}
]

# 验证json格式
def validate_json(json_string, schema):
	try:
		# 解析 JSON 字符串
		data = json.loads(json_string)
		# 使用 jsonschema 验证
		validate(instance=data, schema=schema)
		return True
	except (json.JSONDecodeError, ValidationError) as e:
		return False


def get_score_table(prompt: aitestOrm.PromptComp):
	score_table = tables[prompt.type - 1]
	score = session.query(score_table).filter(score_table.sc_id == prompt.sc_id).first()
	return score

def run_prompt_by_api(prompt: aitestOrm.PromptComp):
	if prompt.comp_id != None:
		print(f"Prompt {prompt.prompt_id} has been complemented.")
		return 0
	score = get_score_table(prompt)
	model_name = score.model_name

	response = "None"
	# 最大重试次数
	max_retries = 5
	wait_time = 30
	retry_count = 0
	success = False
	while retry_count < max_retries and not success:
		try:
			response = call(json.loads(prompt.prompt_json), wait_time)
			success = True  # 请求成功
		except requests.exceptions.Timeout:
			retry_count += 1
			wait_time += 10
			print(f"请求超时，第{retry_count}次重试...")
			time.sleep(2)  # 等待2秒再重试
		except requests.exceptions.ReadTimeout:
			retry_count += 1
			wait_time += 10
			print(f"请求超时，第{retry_count}次重试...")
			time.sleep(2)  # 等待2秒再重试
		except Exception as e:
			print(f"发生错误: {e}")
			exit(0)  # 发生其他错误时停止重试

	if prompt.type >= 3:
		original_response = response
		response = get_json(response)
		max_tries = max_retries - retry_count
		while not validate_json(response, schemas[prompt.type - 3]) and max_tries > 0:
			max_tries -= 1
			original_response = call(json.loads(prompt.prompt_json), wait_time)
			response = get_json(original_response)
		if not validate_json(response, schemas[prompt.type - 3]):
			print(f"Prompt {prompt.prompt_id} complement bad json")
			print(f"response:\n {original_response}")
			response = json.dumps(default_complement[prompt.type - 3], ensure_ascii=False)


	complement_gen = aitestOrm.ComplementGen(content=response)
	session.add(complement_gen)
	session.flush()
	prompt.comp_id = complement_gen.comp_id
	score.comp_id = complement_gen.comp_id
	session.commit()
	print(f"Generate complement for prompt {prompt.prompt_id} successfully. comp_id: {complement_gen.comp_id}")
	return 1

def run_prompt_by_vllm(llm, sampling_params, prompt: aitestOrm.PromptComp):
	conversation = json.loads(prompt.prompt_json)['messages']
	outputs = llm.chat(conversation,
					   sampling_params=sampling_params,
					   use_tqdm=False)
	output = outputs[0]
	generated_text = output.outputs[0].text
	
	if prompt.type >= 3:
		original_text = generated_text
		generated_text = get_json(original_text)
		max_tries = 5
		while not validate_json(generated_text, schemas[prompt.type - 3]) and max_tries > 0:
			max_tries -= 1
			outputs = llm.chat(conversation,
							   sampling_params=sampling_params,
							   use_tqdm=False)
			output = outputs[0]
			original_text = output.outputs[0].text
			generated_text = get_json(original_text)
		if not validate_json(generated_text, schemas[prompt.type - 3]):
			print(f"Prompt {prompt.prompt_id} complement bad json")
			print(f"response:\n {original_text}")
			generated_text = json.dumps(default_complement[prompt.type - 3], ensure_ascii=False)
	complement_gen = aitestOrm.ComplementGen(content=generated_text)
	session.add(complement_gen)
	session.flush()
	prompt.comp_id = complement_gen.comp_id
	table = tables[prompt.type - 1]
	score = session.query(table).filter(table.sc_id == prompt.sc_id).first()
	score.comp_id = complement_gen.comp_id
	session.commit()
	print(f"Generate complement for prompt {prompt.prompt_id} successfully. comp_id: {complement_gen.comp_id}")


	return 1



def run_complement():
	invalid_prompts = 0
	prompts_num = 0
	prompts = session.query(aitestOrm.PromptComp).all()
	for prompt in prompts:
		score_table = tables[prompt.type - 1]
		score = session.query(score_table).filter(score_table.sc_id == prompt.sc_id).first()
		if score is None:
			session.query(aitestOrm.ComplementGen).filter(aitestOrm.ComplementGen.comp_id == prompt.comp_id).delete()
			session.delete(prompt)
			session.commit()
			invalid_prompts += 1
			continue

		if prompt.comp_id != None:
			continue	

		prompts_num += run_prompt_by_api(prompt)

	print(f"Invalid prompts: {invalid_prompts} is deleted.")
	print(f"Generate complement for {prompts_num} prompts successfully.")


def run_complement_for_api_model(model):
	prompts = session.query(aitestOrm.PromptComp).filter(aitestOrm.PromptComp.comp_id == None).all()
	prompts = [prompt for prompt in prompts if json.loads(prompt.prompt_json)['model'] == model]
	for prompt in prompts:
		run_prompt_by_api(prompt)

def run_complement_for_ollama_model(model):
	if not ollama_run(model):
		print("Failed to run model.")
		return

	run_complement_for_api_model(model)

	if not ollama_stop(model):
		print("Failed to stop model.")

def start_run_complement_for_vllm_model(model):
	# 启动推理脚本并等待其完成
	print(f"开始推理：{model}")
	process = subprocess.Popen(
		['python', '-u', 'run_complement_for_vllm_model.py', model],
		stdout=sys.stdout,  # 将标准输出重定向到父进程的标准输出
		stderr=sys.stderr   # 将标准错误重定向到父进程的标准错误
	)
	global son_process
	son_process = process
	process.wait()  # 等待当前推理完成
	son_process = None
	print(f"推理完成：{model}")

def run_complement_for_vllm_model(model):
	config = get_model_config(model)
	model_base_path = config['base_path']

	llm = LLM(model=model_base_path + "/" + model,
		  tensor_parallel_size=2,
		  trust_remote_code=True)
	sampling_params = SamplingParams(
		temperature=0.0,
		top_p=0.95,
		max_tokens=4096,  # 设置最大生成长度
		stop=[]  # 禁用默认的停止序列
	)

	prompts = session.query(aitestOrm.PromptComp).filter(aitestOrm.PromptComp.comp_id == None).all()
	prompts = [prompt for prompt in prompts if json.loads(prompt.prompt_json)['model'] == model]
	for prompt in prompts:
		run_prompt_by_vllm(llm, sampling_params, prompt)


def run_complement_order_by_model():
	models = config['models']
	for model in models:
		print(f"Start to complement for model {model['name']}")
		print('-' * 50)
		prompts = session.query(aitestOrm.PromptComp).filter(aitestOrm.PromptComp.comp_id == None).all()
		prompts = [prompt for prompt in prompts if json.loads(prompt.prompt_json)['model'] == model['name']]
		if len(prompts) > 0:
			if model['api'] == 'openai':
				run_complement_for_api_model(model['name'])
			elif model['api'] == 'dashscope':
				run_complement_for_api_model(model['name'])
			elif model['api'] == 'ollama':
				run_complement_for_ollama_model(model['name'])
			elif model['api'] == 'vllm':
				start_run_complement_for_vllm_model(model['name'])
		else:
			print(f"model {model['name']} has no prompts to complement.")
		print('-' * 50)
		print(f"Complement for model {model['name']} finished.")

def run_complement():
	run_complement_order_by_model()

if __name__ == '__main__':
	run_complement_order_by_model()