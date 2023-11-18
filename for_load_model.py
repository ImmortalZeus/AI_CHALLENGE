import os
os.environ['TRANSFORMERS_CACHE'] = './cache/'
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

import argparse
import pandas as pd

from tools.utils import use_calculator
from dataset import get_data, TestDataset

def get_prompt(message: str, chat_history: list[tuple[str, str]],
               system_prompt: str) -> str:
    texts = [f'[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n']
    #for user_input, response in chat_history:
    #    texts.append(f'{user_input.strip()} [/INST] {response.strip()}[INST] ')
    texts.append(f'{message.strip()} [/INST]')
    return ''.join(texts)

def run(message: str,
        chat_history: list[tuple[str, str]],
        system_prompt: str,
        max_new_tokens: int = 100,
        temperature: float = 0.5,
        top_p: float = 0.95,
        top_k: int = 50) -> Iterator[str]:
    prompt = get_prompt(message, chat_history, system_prompt)
    inputs = tokenizer([prompt], return_tensors='pt').to("cuda")

    streamer = TextIteratorStreamer(tokenizer,
                                    timeout=10.,
                                    skip_prompt=True,
                                    skip_special_tokens=True)
    generate_kwargs = dict(
        inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        top_p=top_p,
        top_k=top_k,
        temperature=temperature,
        num_beams=1,
    )
    t = Thread(target=model.generate, kwargs=generate_kwargs)
    t.start()

    outputs = []
    for text in streamer:
        outputs.append(text)
        yield ''.join(outputs)

def generate(
    message: str,
    history_with_input: list[tuple[str, str]],
    system_prompt: str,
    max_new_tokens: int,
    top_p: float,
    temperature: float,
    top_k: int,
) -> Iterator[list[tuple[str, str]]]:

    history = history_with_input[:-1]
    generator = run(message, history, system_prompt, max_new_tokens,
                    temperature, top_p, top_k)
    try:
        first_response = next(generator)
        yield history + [(message, first_response)]
    except StopIteration:
        yield history + [(message, '')]
    for response in generator:
        yield history + [(message, response)]

def process_example(message: str,
                    system_prompt: str,
                    max_new_tokens: int,
                    top_p: float,
                    temperature: float,
                    top_k: int,) -> tuple[str, list[tuple[str, str]]]:
    generator = generate(
                          message= message,
                          history_with_input= [],
                          system_prompt= system_prompt,
                          max_new_tokens= max_new_tokens,
                          top_p= top_p,
                          temperature= temperature,
                          top_k= top_k,
                          )
    for x in generator:
        pass
    return '', x

import re
def convert_to_submit_file(api_result: str = '', options: str = ''):
    api_result = ((api_result.replace('/s', '')).replace('\n', '')).replace(' ', '')
    api_result = re.sub(r'[^a-zA-Z0-9.:\\)]', '', api_result)
    answer_start = api_result.lower().find(":")
    if answer_start != -1:
        if api_result[-1] == '.':
            api_result = api_result[:-1]
        answer_part = api_result[answer_start + 1:].strip()
        if any(c.isalpha() for c in answer_part):
            answer = answer_part[0:answer_part.find(")")]
            answer =  answer.lower()

        else:
            answer = answer_part.lower()

        if options != '':
            options = options.lower().replace(" ", "")
            if is_number(answer):
              answer_id = options.find(str(answer))
              character_id = options.rfind(')', 0, answer_id)
              answer = options[character_id-1]
            else:
              answer = answer
            #for option in options_lower.split(','):
            #    if ' ' + option.strip() + ' ' in api_result.lower():
            #        return option.strip()
        return answer

    return 'Nan'

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def main(args):
    device = torch.device("cuda")
    tokenizer = AutoTokenizer.from_pretrained(model_name=args.load)
    model = AutoModelForCausalLM.from_pretrained(model_name=args.load, torch_dtype=torch.float32, device_map='auto')
    model.to(device)
    print("Model Loaded")

    data_link = './data/'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
		"--load", type=str, 

		default="WizardLM/WizardMath-7B-V1.0",
		help="Name or path to model"
	)
    parser.add_argument(
		"--testdata", type=str, 

		default="./data/test.json",
		help="Path to test data"
	)
    parser.add_argument(
		"--traindata", type=str, 

		default="./data/train.json",
		help="Path to train data"
	)

    args = parser.parse_args()
    main(args)
