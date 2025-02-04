from http import HTTPStatus
import os
import json
import time
import requests
from database_connect import get_session
import aitestOrm


# 读取配置文件
with open('config.json', 'r') as config_file:
	config = json.load(config_file)

def get_model_config(model: str):
	models = config['models']
	for m in models:
		if m['name'] == model:
			return m
	return None

def ollama_run(model: str):
	config = get_model_config(model)
	url = config['base_url'] + "/chat"
	data = {
		"model": model,
		"messages": []
	}
	response = requests.post(url, json=data)
	if response.status_code == HTTPStatus.OK:
		return response.json()['done']
	else:
		return False

def ollama_stop(model: str):
	config = get_model_config(model)
	url = config['base_url'] + "/chat"
	data = {
		"model": model,
		"messages": [],
		"keep_alive": 0
	}
	response = requests.post(url, json=data)
	if response.status_code == HTTPStatus.OK:
		return response.json()['done']
	else:
		return False

def call_ollama(prompt: dict, wait_time=10):
	config = get_model_config(prompt['model'])
	url = config['base_url'] + "/chat"
	data = {
		"model": prompt["model"],
		"messages": prompt["messages"],
		"stream": False
	}
	try:
		response = requests.post(url, json=data, timeout=wait_time)
		if response.status_code == HTTPStatus.OK:
			return response.json()['message']['content']
		else:
			return None
	except requests.exceptions.RequestException as e:
		raise e

def call_dashscope(prompt: dict, wait_time=10):
	model = prompt['model'] 
	model_config = get_model_config(model)
	api_key = model_config['api_key']
	url = model_config['base_url']

	# 构建请求数据
	data = {
		"model": prompt["model"],
		"input": {
			"messages": prompt["messages"]
		},
		"parameters": {
			"result_format": "text"
		}
	}

	headers = {
		"Authorization": f"Bearer {api_key}",
		"Content-Type": "application/json"
	}

	try:
		response = requests.post(url, headers=headers, data=json.dumps(data), timeout=wait_time)
		response.raise_for_status()  # 检查请求是否成功
		return response.json()['output']['text']
	except requests.exceptions.RequestException as e:
		raise e

def call_openai(prompt: dict, wait_time=10):
	model = prompt['model'] 
	model_config = get_model_config(model)
	api_key = model_config['api_key']
	url = model_config['base_url'] + "/chat/completions"

	# 构建请求数据
	data = {
		"model": prompt["model"],
		"messages": prompt["messages"],
		"response_format": prompt["response_format"]
	}

	headers = {
		"Authorization": f"Bearer {api_key}",
		"Content-Type": "application/json"
	}

	try:
		response = requests.post(url, headers=headers, data=json.dumps(data), timeout=wait_time)
		response.raise_for_status()  # 检查请求是否成功
		return response.json()['choices'][0]['message']['content']
	except requests.exceptions.RequestException as e:
		raise e

def call(prompt: dict, wait_time=10):
	model_config = get_model_config(prompt['model'])
	if model_config['api'] == 'dashscope':
		return call_dashscope(prompt, wait_time)
	elif model_config['api'] == 'openai':
		return call_openai(prompt, wait_time)
	elif model_config['api'] == 'ollama':
		return call_ollama(prompt, wait_time)
	else:
		print("No such api.")
		return None

def test_call_dashscope():
	prompt = {
		"model": "llama3.3-70b-instruct",
		"messages": [{'role': 'system', 'content': 'You are a helpful assistant.'},
					{'role': 'user', 'content': '介绍一下自己'}],
		"response_format": {'type': 'text'}
	}
	print(call_dashscope(prompt))

def test_call_openai():
	prompt = {
		"model": "qwen2.5-7b-instruct",
		"messages": [{'role': 'system', 'content': 'You are a helpful assistant.'},
					{'role': 'user', 'content': '以 JSON 格式介绍一下自己'}],
		"response_format": {'type': 'json_object'}
	}
	print(call_openai(prompt))

def test_ollama(model):
	res = ollama_run(model)
	print(res)
	if res == False:
		print("Failed to run model.")
		return

	while True:
		s = input("Input /bye to exit: ")
		if s == "/bye":
			break
		prompt = {
			"model": model,
			"messages": [{'role': 'user', 'content': s}],
		}
		print(call(prompt))

	res = ollama_stop(model)
	print(res)
	print("Model stopped." if res else "Failed to stop model.")


if __name__ == '__main__':
	#test_call_dashscope()
	#test_call_openai()
	#prompt = {
	#	"model": "moonshot-v1-8k",
	#	"messages": [{'role': 'system', 'content': 'You are a helpful assistant.'},
	#				{'role': 'user', 'content': '以 JSON 格式介绍一下自己'}],
	#	"response_format": {'type': 'text'}
	#}

	#session = get_session('database_aitest')
	#prompt = json.loads(session.query(aitestOrm.PromptComp).filter(aitestOrm.PromptComp.comp_id == None).first().prompt_json)

	##print(prompt)

	#print(call(prompt))

	test_ollama("codellama:13b")