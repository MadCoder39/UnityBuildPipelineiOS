import os
import subprocess

from unity_build_pipeline.Support.logger import color_raw_input, color_print, RESET, YELLOW, RED, GREEN


def run(cmd, cwd=None, silent=False):
    if cwd is None:
        cwd = os.getcwd()
    if silent:
        return try_run(cmd, cwd, silent)
    else:
        color_print("Running command:", YELLOW)
        color_print(' '.join(cmd), YELLOW)
        exit_code = try_run(cmd, cwd, silent)
        if exit_code == 0:
            color_print("Command success!", GREEN)
        else:
            color_print(f"Command failed with code {exit_code}!", RED)
        return exit_code


def try_run(cmd, cwd, silent=False):
    try:
        stdout = subprocess.DEVNULL if silent else None
        exit_code = subprocess.check_call(cmd, cwd=cwd, stdout=stdout)
        return exit_code
    except subprocess.CalledProcessError as e:
        exit_code = e.returncode
        return exit_code


def question_yes_no(q, default_answer='y', color=RESET):
    answer = question(q, default_answer=('y' if default_answer else 'n'), answers=['y', 'n'], color=color)
    return answer == 'y'


def question(question, check_answer=None, incorrect_answer=None, example=None, default_answer=None, answers=None,
             color=RESET):
    def def_check_answer(ans):
        if ans == '' and default_answer is not None:
            return True
        if ans.upper() in answers or ans in answers or ans.lower in answers:
            return True
        return False

    if answers:
        if check_answer is None:
            check_answer = def_check_answer
        answers = list(map(lambda x: x.upper() if x == default_answer else x, answers))
        answers_help = ' [%s]' % '/'.join(answers)
    else:
        if default_answer:
            answers_help = ' [%s]' % default_answer
        else:
            answers_help = ''
    if example:
        answers_help = " (ex. %s)%s" % (example, answers_help)
    actual_question = question + answers_help + ": "

    actual_answer = color_raw_input(actual_question, color)
    if check_answer:
        if incorrect_answer is None:
            incorrect_answer = lambda ans: 'Type one of available answers: %s' % ", ".join(answers)
        answer_correct = check_answer(actual_answer)
        while not answer_correct:
            if incorrect_answer:
                color_print(incorrect_answer(actual_answer), YELLOW)
            actual_answer = color_raw_input(actual_question, color)
            answer_correct = check_answer(actual_answer)
    else:
        answer_correct = True
    if actual_answer == '' and default_answer and answer_correct:
        return default_answer.strip()
    return actual_answer.strip()

class Question:
    @staticmethod
    def _const_false():
        return False

    @classmethod
    def checked_once(cls, question_func, check_func):
        return cls.checked(
            question_func=question_func,
            check_func=check_func,
            retry_func=cls._const_false(),
            retries=1
        )


    @staticmethod
    def decorated_ask_continue(message='', color=RESET):
        message = message or "Command failed; retry?"
        return lambda: question_yes_no(message, color=color)

    @classmethod
    def retry_while_wanna(cls, question_func, check_func, message='', color=RED):
        return cls.checked(
            question_func=question_func,
            check_func=check_func,
            retry_func=cls.decorated_ask_continue(message, color),
        )

    @classmethod
    def checked(cls, question_func, check_func, retry_func, retries=100):
        try_num = 0
        while True:
            try_num += 1
            ans = question_func()
            if check_func(ans):
                return True
            elif try_num >= retries or not retry_func(ans):
                return False



def quiz(q, answers, color=RESET):
    color_print(q, color)
    lst = []

    def __print_variants(ans):
        for i, p in enumerate(answers):
            color_print("[%s] %s" % (i + 1, p,), color)
            lst.append(str(i + 1))
        return '' if ans is None else "\"%s\" is not one of the options numbers!" % ans

    __print_variants(None)
    idx = int(question(
        'Choose one of the options above (Enter the number of the selected option)',
        answers=lst, incorrect_answer=__print_variants, color=color))
    return answers[idx - 1]
