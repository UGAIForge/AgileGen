import AiderModify.ModifyCodeAiderPrompts as prompts
import os
import time
import shutil
import git
import openai
from pathlib import Path
from aider.io import InputOutput
from aider import models
from aider.coders import Coder

def modify_code_aider(user_prompts, edit_purpose, testdir, model_name, edit_format, tries, no_unit_tests, no_aider, verbose, commit_hash):
    testdir = Path(testdir)

    history_fname = os.path.join(testdir, ".aider.chat.history.md")

    timestamp= time.strftime("%Y-%m-%d-%H-%M", time.localtime())
    original_dname = str(testdir) + "_" + timestamp
    print(original_dname)

    if not os.path.exists(original_dname):
        os.makedirs(original_dname)

    fnames = []
    for fname in testdir.glob("*"):
        if "test" not in fname.name and fname.is_file() and fname.name[0] != ".":
            fnames.append(fname)

            # restore the original file, in case we interrupted a prev run
            # after it had saved changes
            original_fname = os.path.join(original_dname, fname.name)
            print(fname, original_fname)
            shutil.copy(fname, original_fname)

    file_list = " ".join(fname.name for fname in fnames)
    
    instructions = user_prompts

    if edit_purpose == "design":
        instructions += prompts.design_instructions
        instructions += prompts.instructions_addendum.format(file_list=file_list)
    elif edit_purpose == "code":
        instructions += prompts.code_instructions
        instructions += prompts.instructions_addendum.format(file_list=file_list)

    io = InputOutput(
        pretty=True,
        yes=False,
        chat_history_file=history_fname,
    )

    main_model = models.Model(model_name)
    edit_format = edit_format or main_model.edit_format

    show_fnames = ",".join(map(str, fnames))
    print("fnames:", show_fnames) # result file name .py

    coder = Coder.create(
                        main_model=main_model,
                        edit_format=edit_format,
                        io=io,
                        fnames=fnames,
                        use_git=False,
                        stream=False,
                        pretty=False,
                        verbose=verbose,
                    )

    timeouts = 0

    dur = 0
    test_outcomes = []
    for i in range(tries):
        start = time.time()
        if not no_aider:
            coder.run(with_message=instructions)
        dur += time.time() - start

        if coder.num_control_c:
            raise KeyboardInterrupt

        if no_unit_tests:
            break


        errors = errors.splitlines()
        print(errors[-1])
        errors = errors[:50]
        errors = "\n".join(errors)
        instructions = errors
        instructions += prompts.test_failures.format(file_list=file_list)


def run_aider():
    testdir = "../static/html"
    model_name="gpt-3.5-turbo-0613"
    edit_format="whole" 
    tries=2 
    no_unit_tests=True 
    no_aider=False 
    verbose=False 
    commit_hash="e3aa9db-dirty"
    edit_purpose = "design" #code 
    # repo = git.Repo(search_parent_directories=True)
    # commit_hash = repo.head.object.hexsha[:7]
    # if repo.is_dirty():
    #     commit_hash += "-dirty"

    modify_code_aider("", edit_purpose, testdir, model_name, edit_format, tries, no_unit_tests, no_aider, verbose, commit_hash)

if __name__ == "__main__":
    # for quick test function
    os.environ["openai_api_key"] = "YOUR API KEY"
    openai_api_base="https://api.openai.com/v1"

    openai.api_key = os.environ["openai_api_key"]
    openai.api_base = openai_api_base

    run_aider()