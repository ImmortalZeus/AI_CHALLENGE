import openai
import argparse
import time 
import re
import random

from dataset import get_data
from convert_image import convert_image
from os.path import isfile, join
import json

def read_jsonl(path: str):
    with open(path) as f:
        data = json.load(f)
        return data

def get_response(args, prompt, max_len, temp):
    responese = openai.Completion.create(
        model = args.model_name,
        # engine = args.model_name,
        prompt = prompt,
        max_tokens = max_len,
        n = 1,
        temperature = temp,
        top_p=0.1,
    )

    return responese

def is_number(string):
    try:
        x = float(string)
        return True
    except Exception:
        return False

def parse_ans(api_result: str = "", text_to_find: str = "", problem: dict = {}):
    if problem["options"] != "": # câu hỏi chọn đáp án đúng
        answer_start = api_result.lower().find(text_to_find.lower())

        if answer_start != -1:
            answer_end = api_result.find(",", answer_start)
            if(answer_end == -1):
                answer_end = len(api_result)
            answer_part = api_result[answer_start + len(text_to_find):answer_end].strip()

            if any(c.isalpha() for c in answer_part):
                answer = answer_part[0:(answer_part.find(")") if answer_part.find(")") != -1 else answer_part.find(":"))]
            else:
                answer = answer_part
            answer = answer.strip()
            if(len(answer) > 1):
                answer = answer[0]
            return answer.lower()
        # else:
        #     answer = api_result
        #     return answer.lower()

        answer_start = api_result.lower().rfind(text_to_find.lower())

        if answer_start != -1:
            answer_end = api_result.find(",", answer_start)
            if(answer_end == -1):
                answer_end = len(api_result)
            answer_part = api_result[answer_start + len(text_to_find):answer_end].strip()

            if any(c.isalpha() for c in answer_part):
                answer = answer_part[0:(answer_part.find(")") if answer_part.find(")") != -1 else answer_part.find(":"))]
            else:
                answer = answer_part
            answer = answer.strip()
            if(len(answer) > 1):
                answer = answer[0]
            return answer.lower()
        # else:
        #     answer = api_result
        #     return answer.lower()
        
        return None
    else: # câu hỏi tự điền đáp án
        answer_start = api_result.lower().rfind(text_to_find.lower())
        if answer_start != -1:
            answer_end = api_result.find(",", answer_start)
            if(answer_end == -1):
                answer_end = len(api_result)
            answer_part = api_result[answer_start + len(text_to_find):answer_end].strip()
            answer = answer_part.split(" ")[0]
            if answer != "" and answer[-1] == ".":
                answer = answer[:-1]
            answer = answer.replace("\\$", "")
            answer = answer.replace("$", "")
            answer = answer.replace("%", "")
            answer = answer.replace("\)", "")
            answer = answer.replace(",", "")
            try:
                if int(float(answer)) == float(answer):
                    answer = str(int(float(answer)))
            except Exception as error:
                pass
            if answer != "" and is_number(answer):
                return answer.lower()
        # else:
        #     answer = api_result
        #     return answer.lower()

        answer_start = api_result.lower().find(text_to_find.lower())

        if answer_start != -1:
            answer_end = api_result.find(",", answer_start)
            if(answer_end == -1):
                answer_end = len(api_result)
            answer_part = api_result[answer_start + len(text_to_find):answer_end].strip()
            answer = answer_part.split(" ")[0]
            if answer != "" and answer[-1] == ".":
                answer = answer[:-1]
            answer = answer.replace("\\$", "")
            answer = answer.replace("$", "")
            answer = answer.replace("%", "")
            answer = answer.replace("\)", "")
            answer = answer.replace(",", "")
            try:
                if int(float(answer)) == float(answer):
                    answer = str(int(float(answer)))
            except Exception as error:
                pass
            if answer != "" and is_number(answer):
                return answer.lower()
        # else:
        #     answer = api_result
        #     return answer.lower()
        
        return None


def convert_to_submit_file(api_result: str = "", problem: dict = {}):
    api_result = api_result.strip()
    api_result = api_result.replace(" , ", " |||| ")
    api_result = api_result.replace(", ", "|||| ")
    api_result = api_result.replace(",", "")
    api_result = api_result.replace(" |||| ", " , ")
    api_result = api_result.replace("|||| ", ", ")
    if problem["options"] != "": # câu hỏi chọn đáp án đúng
        texts = ["Answer:", "Answer :", "Result:", "Result :", "answer is letter :", "result is letter :", "answer is letter:", "result is letter:", "answer is :", "result is :", "answer is:", "result is:", "final answer is", "final result is", "answer is letter", "result is letter", "answer is", "result is", ""]
        for text in texts:
            tmp = parse_ans(api_result=api_result, text_to_find=text, problem=problem)
            if tmp and tmp != "":
                return tmp.split('\n')[0].lower()
        ans = random.choice(problem["options"].split(", "))
        ans = ans.strip()
        return ans[0].lower()
    else: # câu hỏi tự điền đáp án
        texts = [" = ", "=", "Answer:", "Answer :", "Result:", "Result :", "answer is letter :", "result is letter :", "answer is letter:", "result is letter:", "answer is :", "result is :", "answer is:", "result is:", "is :", "is:", "final answer is", "final result is", "answer is letter", "result is letter", "answer is", "result is", "is "]
        for text in texts:
            tmp = parse_ans(api_result=api_result, text_to_find=text, problem=problem)
            if tmp:
                return tmp.split('\n')[0].lower()
        if api_result != "" and api_result[-1] == ".":
            api_result = api_result[:-1]
        api_result = api_result.replace("\\$", "")
        api_result = api_result.replace("$", "")
        api_result = api_result.replace("%", "")
        api_result = api_result.replace("\)", "")
        api_result = api_result.replace(",", "")
        ans = ""
        for word in api_result.split(" "):
            try:
                ans = float(word)
                if int(float(word)) == float(word):
                    ans = str(int(float(word)))
                return str(ans)
            except Exception as error:
                pass
        ans = api_result.strip()
        return ans.split('\n')[0].split(" ")[0].lower()

def main(args):
    with open("openai_api_key.txt", "r") as f:
        openai.api_key = f.readline()

        if not args.resume_from_checkpoint:
            open('./results/results.txt', 'w').close()

        test_examples = get_data(args.data)
        results = []
        with open('./results/results.txt', 'r') as read:
            results = read.readlines()
        last_indx = len(results)
        print("Last request: ", last_indx)

        converted_images = dict()
        try:
            converted_images = read_jsonl('converted_images.json')
            if(str(converted_images) == ""):
                converted_images = dict()
        except Exception:
            converted_images = dict()

        with open('./results/results.txt', 'a') as f:
            i = 0
            while i < len(test_examples):
                # if i >= 510: # chỉ trả lời 100 câu
                #     break
                if i >= last_indx:
                    try:
                        problem = test_examples[i]
                        prompt = ""
                        nl = '\n'
                        imagelatex = ""
                        if problem["diagramRef"] != "":
                            if problem["diagramRef"] in converted_images:
                                imagelatex = converted_images[problem["diagramRef"]]
                            if imagelatex == "":
                                try:
                                    imagelatex = str(convert_image(join("./diagrams/diagrams/", problem["diagramRef"])))
                                    if imagelatex and imagelatex != "":
                                        imagelatex = "The image can be described form of LaTeX as follow : " + str(imagelatex) + "\n"
                                    else:
                                        imagelatex = ""
                                except Exception:
                                    imagelatex = ""
                        if problem["options"] != "": # câu hỏi chọn đáp án đúng
                            prompt = f"Find the CORRECT answer for the following MATH problem .\nThe problem is : {problem['Problem'].strip()}\n${imagelatex}There are {len(problem['options'].strip().split(','))} choices :\n{' , '.join([e.strip().replace(' )', ')') for e in problem['options'].strip().split(',')])}\nNote that you only need to give me the letter corresponding to the correct chosen answer ."
                        else: # câu hỏi tự điền đáp án
                            prompt = f"Find the correct answer for the following complicated MATH problem : {problem['Problem'].strip()}\n{'The problem is described in LaTeX format . ' if ('$' in problem['Problem']) else ''}\n${imagelatex}Note that you DO NOT need to tell me how you solved it , just return a single human-readable number as the answer ( NOT in LaTeX ) ."
                        max_len = 40
                        temp = 0.12
                        responese = {}
                        t1 = time.time()
                        responese = get_response(args, prompt, max_len, temp)
                        t2 = time.time()
                        # print(prompt)
                        time_request = t2 - t1
                        answer = responese.choices[0].text
                        #results.append([answer, time_request])
                    except Exception as error:
                        print("Waiting...")
                        print(error)
                        # i -= 1
                        time.sleep(20)
                        continue
                    print(f"Time request for {problem['id']}: {time_request}, answer: {answer}")
                    choose = str(convert_to_submit_file(answer, problem)).strip().lower()
                    f.write(choose + '\t' + str(time_request) + '\n')
                    print(str(i + 1) + ") " + choose + '\t' + str(time_request) + '\n')
                    # time.sleep(1)

                i += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
		"--model_name", type=str,
		default="gpt-3.5-turbo-instruct",
        help= "Name to request model from openai"
	)
    parser.add_argument(
		"--data", type=str,
		default="./data/test.json",
		help="Path to data test"
	)
    parser.add_argument(
		"--resume_from_checkpoint", type=bool,
		default=True,
		help="Resume from checkpoint"
	)

    args = parser.parse_args()
    main(args)