from openai import OpenAI
import json

# 示例字符串
json_string = '{"code": "12345"}'




client = OpenAI(
	api_key = "sk-p2jw2UiU3Feg1tqAI5utnkcpR7KyOuUAKjd35crNafvIv07c",
    base_url="https://api.moonshot.cn/v1",
)
 

 

json_str = session.query(aitestOrm.PromptEval).filter(aitestOrm.PromptEval.type == 2).first().prompt_json
print(json_str)

params = json.loads(json_str)

response = client.chat.completions.create(**params)
 
# stream=False的时候，打开这个，启用非流式返回
print(response.choices[0].message.content)
