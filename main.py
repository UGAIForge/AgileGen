import sys
import time
import os
import gradio as gr
from utils.log import Logger
from pathlib import Path
from utils.CodeGeneration import CodeGeneration
from utils.utils import zip_folder, iframe_generator
from database.DB_Tools import DB_Tools
from dotenv import load_dotenv
from AiderModify.ModifyCodeAider import modify_code_aider

# ----------log-------------
sys.stdout = Logger("logs/logs.log")
load_dotenv()

if __name__ == "__main__":

    codegeneration = CodeGeneration()
    db_tools = DB_Tools()

    def read_logs():
        sys.stdout.flush()
        with open("logs/logs.log", "r") as f:
            return f.read()
    # ----------log----------------

    # create a static directory to store the static files
    static_dir = Path(codegeneration.args.static_dir)
    static_dir.mkdir(parents=True, exist_ok=True)
    #

    def fn_scenario_generation(input_feature):
        feature2scenarios_list = db_tools.select_all()
        similar_Feature2Scenarios = codegeneration.TopN_Feature2Scenarios(
            feature2scenarios_list, input_feature)
        print("\n------------------Gherkin generating-------------------\n")
        Gherkin_response, messages = codegeneration.Gherkin_generation(input_feature, similar_Feature2Scenarios)
        print(Gherkin_response)
        Scenarios_List = codegeneration.Scenario_Parsing(Gherkin_response)
        print("\n---------------------Gherkin2NL-----------------------\n")
        Gherkin_NL_List = codegeneration.Gherkin2NL(Scenarios_List, messages)
        print(Gherkin_NL_List)

        output_dict = {}
        for i in range(len(Gherkin_NL_List)):
            output_dict[globals()["scenarios_list"][i]
                        ] = gr.update(visible=True)
            output_dict[globals()["scenarios_list"][i].children[0].children[0]] = gr.update(
                value=Gherkin_NL_List[i])
        for i in range(codegeneration.args.max_scenarios_number-len(Gherkin_NL_List)):
            output_dict[globals()["scenarios_list"]
                        [i+len(Gherkin_NL_List)]] = gr.update(visible=False)
            output_dict[globals()["scenarios_list"][i+len(Gherkin_NL_List)
                                                    ].children[0].children[0]] = gr.update(value="")
        output_dict[globals()["scenario_add"]] = gr.update(visible=True)
        output_dict[globals()["code_output"]] = gr.update(visible=False)
        return output_dict

    def fn_scenario_add(*arg):
        print("fn_scenario_add")

        input_string = arg[-1]
        scenarios_string_list = list(arg[:-1])
        for i in range(codegeneration.args.max_scenarios_number):
            if scenarios_string_list[i] == "":
                return {globals()["scenarios_list"][i]: gr.update(visible=True), 
                        globals()["scenarios_list"][i].children[0].children[0]: input_string}

    def fn_code_generation(*args):
        print("\n------------------fn_code_generation-----------------------\n")
        codegeneration.clear_static_html_dir()

        Gherkin_NL_List = []
        for i in range(len(args)-1):
            if args[i] != "":
                Gherkin_NL_List.append(args[i])

        input_feature = args[-1]

        db_tools.insert(input_feature, Gherkin_NL_List)
        print("\n------------------NL2Gherkin-----------------------\n")
        Gherkin_result = codegeneration.NL2Gherkin(Gherkin_NL_List, input_feature)
        print(Gherkin_result)
        time.sleep(15)
        print("\n----------------Design_page_template_generation----------------\n")
        Design_page_template = codegeneration.Design_page_template_generation(Gherkin_result)
        print(Design_page_template)
        print("\n----------------Visual_design_template_generation---------------\n")
        Visual_design_template = codegeneration.Visual_design_template_generation(Design_page_template)
        print(Visual_design_template)
        print("\n----------------Code_generation-----------------\n")
        Generated_code, loop_number = codegeneration.Code_generation(
            Visual_design_template, Design_page_template, input_feature, Gherkin_result)

        file_path = "static/html/index.html"+'?time='+str(time.time())
        file_name = "index.html"
        link = f'<a href="file={file_path}" target="_blank">{file_name}</a>'

        iframe = iframe_generator(file_path)

        output_path = os.path.join(static_dir, "html.zip")
        zip_folder(folder_path=codegeneration.args.static_html_dir,
                   output_path=output_path)

        return link, gr.update(visible=True), output_path, Generated_code, iframe

    def fn_download_file():
        output_path = os.path.join(static_dir, "html.zip")
        zip_folder(folder_path=codegeneration.args.static_html_dir,
                   output_path=output_path)
        return output_path

    def fn_code_modification(code_modification_suggestion_string, generated_code):
        codegeneration.clear_static_html_dir()
        print("Code_Modification")
        modified_code, messages, loop_number = codegeneration.Code_Modification(
            generated_code, code_modification_suggestion_string)
        output_path = os.path.join(static_dir, "html.zip")
        zip_folder(folder_path=codegeneration.args.static_html_dir,
                   output_path=output_path)

        file_path = "static/html/index.html"+'?time='+str(time.time())
        file_name = "index.html"
        link = f'<a href="file={file_path}" target="_blank">{file_name}</a>'
        iframe = iframe_generator(file_path)

        return link, output_path, modified_code, iframe

    def fn_code_modification_aider(code_modification_suggestion_string, generated_code):
        time.sleep(15)
        print("\n---------------Code_Modification-------------\n")
        testdir = "static/html"
        model_name = "gpt-4-turbo-2024-04-09"
        # model_name = "gpt-4o"
        edit_format = "whole"
        tries = 2
        no_unit_tests = True
        no_aider = False
        verbose = False
        commit_hash = "e3aa9db-dirty"
        edit_purpose = "code"
        modify_code_aider(code_modification_suggestion_string, edit_purpose, testdir,
                          model_name, edit_format, tries, no_unit_tests, no_aider, verbose, commit_hash)

        output_path = os.path.join(static_dir, "html.zip")
        zip_folder(folder_path=codegeneration.args.static_html_dir,
                   output_path=output_path)

        file_path = "static/html/index.html"+'?time='+str(time.time())
        file_name = "index.html"
        link = f'<a href="file={file_path}" target="_blank">{file_name}</a>'
        iframe = iframe_generator(file_path)
        modified_code = ""

        return link, output_path, modified_code, iframe

    def fn_design_modification(code_modification_suggestion_string, generated_code):
        codegeneration.clear_static_html_dir()
        print("\n--------------Design_Modification---------------\n")
        modified_code, messages, loop_number = codegeneration.Design_Modification(
            generated_code, code_modification_suggestion_string)
        output_path = os.path.join(static_dir, "html.zip")
        zip_folder(folder_path=codegeneration.args.static_html_dir,
                   output_path=output_path)

        file_path = "static/html/index.html"+'?time='+str(time.time())
        file_name = "index.html"
        link = f'<a href="file={file_path}" target="_blank">{file_name}</a>'
        iframe = iframe_generator(file_path)

        return link, output_path, modified_code, iframe

    def fn_design_modification_aider(code_modification_suggestion_string, generated_code):
        print("\n----------------Design_Modification----------------\n")

        testdir = "static/html"
        model_name = "gpt-4-turbo-2024-04-09"
        edit_format = "whole"
        tries = 2
        no_unit_tests = True
        no_aider = False
        verbose = False
        commit_hash = "e3aa9db-dirty"
        edit_purpose = "code"
        modify_code_aider(code_modification_suggestion_string, edit_purpose, testdir,
                          model_name, edit_format, tries, no_unit_tests, no_aider, verbose, commit_hash)

        output_path = os.path.join(static_dir, "html.zip")
        zip_folder(folder_path=codegeneration.args.static_html_dir,
                   output_path=output_path)

        file_path = "static/html/index.html"+'?time='+str(time.time())
        file_name = "index.html"
        link = f'<a href="file={file_path}" target="_blank">{file_name}</a>'
        iframe = iframe_generator(file_path)
        modified_code = ""

        return link, output_path, modified_code, iframe
    

    with gr.Blocks(title="AgileGen") as app:
        gr.Markdown("# AgileGen")
        generated_code_state = gr.State(value="")

        with gr.Row() as Feature_Block:
            feature_textbox = gr.Textbox(label="Your Feature", lines=3, placeholder="Please input your feature here...", scale=9)
            scenario_generation_btn = gr.Button(value="Scenario Generation", scale=1)

        scenarios_list = []
        scenarios_textbox_list = []

        with gr.Column() as Scenarios_Block:
            with gr.Box():
                for i in range(codegeneration.args.max_scenarios_number):
                    if i < codegeneration.args.init_visible_scenarios_number:
                        with gr.Row(visible=True) as globals()["scenario_{i}"]:
                            globals()["scenario_textbox_{i}"] = gr.Textbox(
                                interactive=True, label=f"Scenario", lines=2, scale=9)
                            globals()["del_btn_{i}"] = gr.Button(
                                value="Del", scale=1)

                            def change_vis():
                                return gr.update(value=""), gr.update(visible=False)
                            
                            globals()["del_btn_{i}"].click(fn=change_vis, inputs=None, outputs=[
                                globals()["scenario_textbox_{i}"], globals()["scenario_{i}"]])
                    else:
                        with gr.Row(visible=False) as globals()["scenario_{i}"]:
                            globals()["scenario_textbox_{i}"] = gr.Textbox(
                                interactive=True, label=f"Scenario", lines=2, scale=9)
                            globals()["del_btn_{i}"] = gr.Button(
                                value="Del", scale=1)

                            def change_vis():
                                return gr.update(value=""), gr.update(visible=False)
                            
                            globals()["del_btn_{i}"].click(fn=change_vis, inputs=None, outputs=[
                                globals()["scenario_textbox_{i}"], globals()["scenario_{i}"]])

                    scenarios_list.append(globals()["scenario_{i}"])
                    scenarios_textbox_list.append(
                        globals()["scenario_textbox_{i}"])

            with gr.Column(visible=False) as globals()["scenario_add"]:
                with gr.Row():
                    globals()["scenario_add_textbox"] = gr.Textbox(
                        interactive=True, label="Your new scenario:", lines=2, scale=9)
                    scenario_add_btn = gr.Button(value="Add", scale=1)
                code_generation_btn = gr.Button(value="Code Generation")

                html_markdown = gr.Markdown(label="Output HTML")

            with gr.Column(visible=False) as globals()["code_output"]:
                with gr.Column():
                    gr_download_file = gr.File()
                    pass
                with gr.Row():
                    globals()["design_modification_textbox"] = gr.Textbox(
                        label="Design Modification Suggestions", scale=9)
                    code_design_modification_btn = gr.Button(
                        value="Design Modification", scale=1)
                with gr.Row():
                    globals()["code_modification_textbox"] = gr.Textbox(
                        label="Code Modification Suggestions", scale=9)
                    code_modification_btn = gr.Button(
                        value="Code Modification", scale=1)

        scenario_generation_btn_outputs = []
        scenario_generation_btn_outputs = scenarios_list+scenarios_textbox_list
        scenario_generation_btn_outputs.append(globals()["scenario_add"])
        scenario_generation_btn_outputs.append(globals()["code_output"])
        scenario_generation_btn.click(
            fn=fn_scenario_generation, inputs=feature_textbox, outputs=scenario_generation_btn_outputs)

        scenario_add_btn_inputs = []
        scenario_add_btn_inputs.extend(scenarios_textbox_list)
        scenario_add_btn_inputs.append(globals()["scenario_add_textbox"])
        scenario_add_btn_outputs = []
        scenario_add_btn_outputs = scenarios_list+scenarios_textbox_list
        scenario_add_btn_outputs.append(globals()["scenario_add"])

        scenario_add_btn.click(
            fn=fn_scenario_add, inputs=scenario_add_btn_inputs, outputs=scenario_add_btn_outputs)

        code_generation_btn_inputs = []
        code_generation_btn_inputs.extend(scenarios_textbox_list)
        code_generation_btn_inputs.append(feature_textbox)

        new_logs = gr.Textbox(label="Log", max_lines=20)
        app.load(read_logs, None, new_logs, every=3, queue=True, scroll_to_output=True)

        code_generation_btn.click(fn=fn_code_generation, inputs=code_generation_btn_inputs, outputs=[
                                  html_markdown, globals()["code_output"], gr_download_file, generated_code_state])

        code_modification_btn.click(fn=fn_code_modification_aider, inputs=[globals()[
                                    "code_modification_textbox"], generated_code_state], outputs=[html_markdown, gr_download_file, generated_code_state])

        code_design_modification_btn.click(fn=fn_design_modification_aider, inputs=[globals(
        )["design_modification_textbox"], generated_code_state], outputs=[html_markdown, gr_download_file, generated_code_state])

    app.queue()
    app.launch()
