import argparse
from runComplement import run_prompt_by_vllm, run_complement_for_vllm_model
import signal

# 定义信号处理函数
def handle_signal(signum, frame):
	print(f"子进程收到信号 {signum}，正在终止...")
	exit(0)

# 注册信号处理
signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)


def main():

	# 解析命令行参数
	parser = argparse.ArgumentParser(description="使用 vllm 进行离线推理")
	parser.add_argument('model', type=str, help="本地模型路径")
	args = parser.parse_args()

	model = args.model

	run_complement_for_vllm_model(model)


if __name__ == '__main__':
	main()