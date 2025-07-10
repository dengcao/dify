import json
import logging
import time
from collections.abc import Generator
from copy import deepcopy
from typing import Any, Optional, cast

from dify_plugin.entities.agent import AgentInvokeMessage
from dify_plugin.entities.model import ModelFeature
from dify_plugin.entities.model.llm import (
    LLMModelConfig,
    LLMResult,
    LLMResultChunk,
    LLMUsage,
)
from dify_plugin.entities.model.message import (
    AssistantPromptMessage,
    PromptMessage,
    PromptMessageContentType,
    SystemPromptMessage,
    ToolPromptMessage,
    UserPromptMessage,
)
from dify_plugin.entities.tool import LogMetadata, ToolInvokeMessage, ToolProviderType
from dify_plugin.interfaces.agent import (
    AgentModelConfig,
    AgentStrategy,
    ToolEntity,
    ToolInvokeMeta,
)
from pydantic import BaseModel


class FunctionCallingParams(BaseModel):
    query: str
    instruction: str | None
    model: AgentModelConfig
    tools: list[ToolEntity] | None
    maximum_iterations: int = 3


class EnhancingFunctionAgentAgentStrategy(AgentStrategy):
    query: str = ""
    instruction: str | None = ""

    @property
    def _user_prompt_message(self) -> UserPromptMessage:
        return UserPromptMessage(content=self.query)

    def _system_prompt_message(self, prompt) -> SystemPromptMessage:
        return SystemPromptMessage(content=prompt)

    def planning(self):
        agent = self.session.model.llm.invoke(
            model_config=self.model_config,
            prompt_messages=[SystemPromptMessage(content="You are a helpful assistant."),
                             UserPromptMessage(content="""You need to decompose a complex user's question into some simple subtasks and let the model execute it step by step.\n
        This is the user's question: %s \n
        Please note that: \n
        1. You should only decompose this complex user's question into some simple subtasks which can be executed easily by using a single tool.\n
        2. Each simple subtask should be expressed into natural language.\n
        3. Each subtask should contain the necessary information from the original question and should be complete, explicit and self-consistent.\n
        4. You must ONLY output the ID of the tool you chose in a parsible JSON format. An example output looks like:\n
        {{\"Tasks\": [\"Task 1\", \"Task 2\", ...]}}\n
        Output:""" % self.query)],
            stop=self.stop,
            stream=False,
        )
        result = agent.message.content
        result = eval(result.replace('`json', '').replace('`', ''))
        tasks = result["Tasks"]
        task_ls = []
        for t in range(len(tasks)):
            task_ls.append({"task": tasks[t], "id": t + 1})
        return task_ls

    def task_topology(self, task_ls):
        ind = 0
        while True:
            try:
                agent = self.session.model.llm.invoke(
                    model_config=self.model_config,
                    prompt_messages=[
                        SystemPromptMessage(content="You are a helpful assistant."),
                        UserPromptMessage(content="""Given a complex user's question, I have decompose this question into some simple subtasks
                I think there exists a logical connections and order amontg the tasks. 
                Thus you need to help me output this logical connections and order.\n
                You must ONLY output in a parsible JSON format with the following format:\n
                [{{\"task\": task, \"id\", task_id, \"dep\": [dependency_task_id1, dependency_task_id2, ...]}}]\n
                The \"dep\" field denotes the id of the previous task which generates a new resource upon which the current task depends. If there are no dependencies, set \"dep\" to -1.\n\n
                This is user's question: %s\n
                These are subtasks of this question:\n
                %s\n
                Output: """ % (self.query, task_ls))],
                    stop=self.stop,
                    stream=False,
                )
                result = agent.message.content
                result = eval(result.replace('`json', '').replace('`', ''))
                for i in range(len(result)):
                    if isinstance(result[i]['dep'], str):
                        temp = []
                        for ele in result[i]['dep'].split(','):
                            temp.append(int(ele))
                        result[i]['dep'] = temp
                    elif isinstance(result[i]['dep'], int):
                        result[i]['dep'] = [result[i]['dep']]
                    elif isinstance(result[i]['dep'], list):
                        temp = []
                        for ele in result[i]['dep']:
                            temp.append(int(ele))
                        result[i]['dep'] = temp
                    elif result[i]['dep'] == -1:
                        result[i]['dep'] = [-1]
                # a = result[i]['dep'][0]
                return result
            except Exception as e:
                print(f"task topology fails: {e}")
                if ind > 5:
                    return -1
                ind += 1
                continue

    def choose_tool(self, question, tool_dic, tool_used):
        clean_answer = []
        ind = 0
        Tool_list = []
        for ele in tool_dic:
            for key in ele.keys():
                if str(key) not in tool_used:
                    Tool_list.append(f'''ID: {key}\n{ele[key]}''')
        while True:
            try:
                agent = self.session.model.llm.invoke(
                    model_config=self.model_config,
                    prompt_messages=[
                        SystemPromptMessage(
                            content="You are a helpful assistant."),
                        UserPromptMessage(content="""This is the user's question: %s\n
            These are the tools you can select to solve the question:\n
            Tool List:\n
            %s\n\n
            Please note that: \n
            1. You should only choice tool in the Tool List to solve this question.\n
            2. You must ONLY output the ID of the tool you chose in a parsible JSON format. An example output looks like:\n
            '''\n"
            Example: [{"ID": XX}]\n"
            '''\n"
            Output:""" % (question, tool_dic))],
                    stop=self.stop,
                    stream=False,
                )
                result = agent.message.content
                clean_answer = eval(result.replace('`json', '').replace('`', '').split("\n\n")[-1].strip())
                clean_answer = [i['ID'] for i in clean_answer]
                break
            except Exception as e:
                print(f"choose tool fails: {e}")
                if ind > 5:
                    return []
                ind += 1
                continue
        return clean_answer


    def tool_check(self, tool_dic):
        agent = self.session.model.llm.invoke(
            model_config=self.model_config,
            prompt_messages=[
                SystemPromptMessage(
                    content="You are a helpful language model which can use external APIs to solve user's question."),
                UserPromptMessage(content="""As a powerful language model, you're equipped to answer user's question with accumulated knowledge. 
            However, in some cases, you need to use external Tools to answer accurately. Please check if there are any matching tools.
            Tool List:\n
            %s\n\n
            Thus, you need to check whether the user's question requires you to call an external Tool to solve it.\n
            Here are some tips to help you check: \n
            1. If the user's question requires real-time information, since your knowledge base isn't updated in real-time, any such question will demand an Tool call.\n
            2. If you need to obtain information (e.g., ID, name, phone number, geographical location, rank, etc.), you need to call the database Tools if you are not sure.\n
            3. If the question demand a database search or internet research to generate an answer, this is another situation where an Tool call is necessary.\n
            4. If the user asks you for history messages, you don't need to use tools. \n
            If need, please output 'YES'; If not, please output 'NO'\n
            You need to give reasons first and then decide whether to keep it or not. You must only output in a parsible JSON format. Two example outputs look like:\n
            Example 1: {{\"Reason\": \"The reason why you think you do not need to call an external Tool to solve the user's question\", \"Choice\": \"No\"}}\n
            Example 2: {{\"Reason\": \"The reason why you think you need to call an external Tool to solve the user's question\", \"Choice\": \"Yes\"}}\n
            This is the user's question: %s\n
            Output:""" % (tool_dic,self.query))],
            stop=self.stop,
            stream=False,
        )
        ind = 0
        result = ''
        while True:
            try:
                result = agent.message.content
                result = eval(result.replace('`json', '').replace('`', ''))
                a = result["Reason"]
                b = result["Choice"]
                print(a, b)
                if 'yes' in b.lower():
                    return result, True
                else:
                    return result, False
            except Exception as e:
                print(f"tool check fails: {e}")
                if ind > 10:
                    return "", False
                ind += 1
                continue
        return result, False

    def make_EASYTOOL_PROMPT(self,task_ls, tool_dic):
        content = """
            This is the user's question: %s
            I already think how to use tools to solve it. 
            the following is the content of task:
            """ % self.query
        tool_used = []
        for task_dic in task_ls:
            tool_ids = self.choose_tool(task_dic['task'], tool_used=tool_used, tool_dic=tool_dic)
            tool_used.extend(tool_ids)
            task_dic['tool_ids'] = tool_ids

        for idx, task_dic in enumerate(task_ls):
            idx += 1
            content += 'task ID: {}. {}\n'.format(idx, task_dic['task'])
            if len(task_dic['tool_ids']) > 0:
                content += 'The available tools include: \n'
                for j in task_dic['tool_ids']:
                    content += f'tool_name: {tool_dic[j]['name']}, description: {tool_dic[j]['Description']} \n'
            if task_dic["dep"] == [-1]:
                content += ''
            else:
                content += 'The pre dependent task ID include: {}'.format(','.join([str(i) for i in task_dic['dep']]))
            content += '\n'
        content += "Based on the above task details, please output the appropriate result based on the user's question"
        return content

    def _invoke(
            self, parameters: dict[str, Any]
    ) -> Generator[AgentInvokeMessage, None, None]:
        """
        Run FunctionCall agent application
        """
        fc_params = FunctionCallingParams(**parameters)

        # init prompt messages
        query = fc_params.query
        self.query = query
        self.instruction = fc_params.instruction

        # convert tool messages
        tools = fc_params.tools
        tool_instances = {tool.identity.name: tool for tool in tools} if tools else {}
        prompt_messages_tools = self._init_prompt_tools(tools)

        # init model parameters
        stream = (
            ModelFeature.STREAM_TOOL_CALL in fc_params.model.entity.features
            if fc_params.model.entity and fc_params.model.entity.features
            else False
        )
        model = fc_params.model
        stop = (
            fc_params.model.completion_params.get("stop", [])
            if fc_params.model.completion_params
            else []
        )

        # init function calling state
        iteration_step = 1
        max_iteration_steps = fc_params.maximum_iterations
        current_thoughts: list[PromptMessage] = []
        function_call_state = True  # continue to run until there is not any tool call
        llm_usage: dict[str, Optional[LLMUsage]] = {"usage": None}
        final_answer = ""


        round_started_at = time.perf_counter()
        round0_log = self.create_log_message(
            label=f"THINKING",
            data={},
            metadata={
                LogMetadata.STARTED_AT: round_started_at,
            },
            status=ToolInvokeMessage.LogMessage.LogStatus.START,
        )
        yield round0_log

        # Refer to a part of the thinking in `EASYTOOL: Enhancing LLM-based Agents with Concise Tool Instruction`
        # https://arxiv.org/pdf/2401.06201
        self.stop = stop
        self.model_config = LLMModelConfig(**model.model_dump(mode="json"))
        tool_dic = [{'ID': idx, "Description": message.description, 'name': message.name} for idx, message in
                    enumerate(prompt_messages_tools)]

        _, ai_use_tool = self.tool_check(tool_dic=tool_dic)
        if ai_use_tool:
            task_ls = self.planning()
            task_ls = self.task_topology(task_ls=task_ls)
            EASYTOOL_PROMPT = self.make_EASYTOOL_PROMPT(task_ls=task_ls, tool_dic=tool_dic)
        else:
            EASYTOOL_PROMPT = ''

        history_prompt_messages = fc_params.model.history_prompt_messages
        history_prompt_messages.insert(0, self._system_prompt_message(self.instruction + '\n' + EASYTOOL_PROMPT))
        history_prompt_messages.append(self._user_prompt_message)


        yield self.finish_log_message(
            log=round0_log,
            data={
                "output": {
                    "easytool_prompt": EASYTOOL_PROMPT,
                },
            },
            metadata={
                LogMetadata.STARTED_AT: round_started_at,
                LogMetadata.FINISHED_AT: time.perf_counter(),
                LogMetadata.ELAPSED_TIME: time.perf_counter() - round_started_at,
            },
        )
        while function_call_state and iteration_step <= max_iteration_steps:
            # start a new round
            function_call_state = False
            round_started_at = time.perf_counter()
            round_log = self.create_log_message(
                label=f"ROUND {iteration_step}",
                data={},
                metadata={
                    LogMetadata.STARTED_AT: round_started_at,
                },
                status=ToolInvokeMessage.LogMessage.LogStatus.START,
            )
            yield round_log

            # If max_iteration_steps=1, need to execute tool calls
            if iteration_step == max_iteration_steps and max_iteration_steps > 1:
                # the last iteration, remove all tools
                prompt_messages_tools = []

            # recalc llm max tokens
            prompt_messages = self._organize_prompt_messages(
                history_prompt_messages=history_prompt_messages,
                current_thoughts=current_thoughts,
            )
            if model.entity and model.completion_params:
                self.recalc_llm_max_tokens(
                    model.entity, prompt_messages, model.completion_params
                )
            # invoke model
            model_started_at = time.perf_counter()
            model_log = self.create_log_message(
                label=f"{model.model} Thought",
                data={},
                metadata={
                    LogMetadata.STARTED_AT: model_started_at,
                    LogMetadata.PROVIDER: model.provider,
                },
                parent=round_log,
                status=ToolInvokeMessage.LogMessage.LogStatus.START,
            )
            yield model_log
            model_config = LLMModelConfig(**model.model_dump(mode="json"))
            # print("prompt_messages: ", prompt_messages)
            chunks: Generator[LLMResultChunk, None, None] | LLMResult = (
                self.session.model.llm.invoke(
                    model_config=model_config,
                    prompt_messages=prompt_messages,
                    stop=stop,
                    stream=stream,
                    tools=prompt_messages_tools,
                )
            )
            tool_calls: list[tuple[str, str, dict[str, Any]]] = []

            # save full response
            response = ""

            # save tool call names and inputs
            tool_call_names = ""

            current_llm_usage = None

            if isinstance(chunks, Generator):
                for chunk in chunks:
                    # print("chunk, ", chunk)
                    # check if there is any tool call
                    if self.check_tool_calls(chunk):
                        function_call_state = True
                        tool_calls.extend(self.extract_tool_calls(chunk) or [])
                        tool_call_names = ";".join(
                            [tool_call[1] for tool_call in tool_calls]
                        )

                    if chunk.delta.message and chunk.delta.message.content:
                        if isinstance(chunk.delta.message.content, list):
                            for content in chunk.delta.message.content:
                                response += content.data
                                if (
                                        not function_call_state
                                        or iteration_step == max_iteration_steps
                                ):
                                    yield self.create_text_message(content.data)
                        else:
                            response += str(chunk.delta.message.content)
                            if (
                                    not function_call_state
                                    or iteration_step == max_iteration_steps
                            ):
                                yield self.create_text_message(
                                    str(chunk.delta.message.content)
                                )

                    if chunk.delta.usage:
                        self.increase_usage(llm_usage, chunk.delta.usage)
                        current_llm_usage = chunk.delta.usage

            else:
                result = chunks
                result = cast(LLMResult, result)
                # check if there is any tool call
                if self.check_blocking_tool_calls(result):
                    function_call_state = True
                    tool_calls.extend(self.extract_blocking_tool_calls(result) or [])
                    tool_call_names = ";".join(
                        [tool_call[1] for tool_call in tool_calls]
                    )

                if result.usage:
                    self.increase_usage(llm_usage, result.usage)
                    current_llm_usage = result.usage

                if result.message and result.message.content:
                    if isinstance(result.message.content, list):
                        for content in result.message.content:
                            response += content.data
                    else:
                        response += str(result.message.content)

                if not result.message.content:
                    result.message.content = ""
                if isinstance(result.message.content, str):
                    yield self.create_text_message(result.message.content)
                elif isinstance(result.message.content, list):
                    for content in result.message.content:
                        yield self.create_text_message(content.data)

            yield self.finish_log_message(
                log=model_log,
                data={
                    "output": response,
                    "tool_name": tool_call_names,
                    "tool_input": [
                        {"name": tool_call[1], "args": tool_call[2]}
                        for tool_call in tool_calls
                    ],
                },
                metadata={
                    LogMetadata.STARTED_AT: model_started_at,
                    LogMetadata.FINISHED_AT: time.perf_counter(),
                    LogMetadata.ELAPSED_TIME: time.perf_counter() - model_started_at,
                    LogMetadata.PROVIDER: model.provider,
                    LogMetadata.TOTAL_PRICE: current_llm_usage.total_price
                    if current_llm_usage
                    else 0,
                    LogMetadata.CURRENCY: current_llm_usage.currency
                    if current_llm_usage
                    else "",
                    LogMetadata.TOTAL_TOKENS: current_llm_usage.total_tokens
                    if current_llm_usage
                    else 0,
                },
            )
            assistant_message = AssistantPromptMessage(content="", tool_calls=[])
            if not tool_calls:
                assistant_message.content = response
                current_thoughts.append(assistant_message)

            final_answer += response + "\n"

            # call tools
            tool_responses = []
            for tool_call_id, tool_call_name, tool_call_args in tool_calls:
                current_thoughts.append(
                    AssistantPromptMessage(
                        content="",
                        tool_calls=[
                            AssistantPromptMessage.ToolCall(
                                id=tool_call_id,
                                type="function",
                                function=AssistantPromptMessage.ToolCall.ToolCallFunction(
                                    name=tool_call_name,
                                    arguments=json.dumps(
                                        tool_call_args, ensure_ascii=False
                                    ),
                                ),
                            )
                        ],
                    )
                )
                tool_instance = tool_instances[tool_call_name]
                tool_call_started_at = time.perf_counter()
                tool_call_log = self.create_log_message(
                    label=f"CALL {tool_call_name}",
                    data={},
                    metadata={
                        LogMetadata.STARTED_AT: time.perf_counter(),
                        LogMetadata.PROVIDER: tool_instance.identity.provider,
                    },
                    parent=round_log,
                    status=ToolInvokeMessage.LogMessage.LogStatus.START,
                )
                yield tool_call_log
                if not tool_instance:
                    tool_response = {
                        "tool_call_id": tool_call_id,
                        "tool_call_name": tool_call_name,
                        "tool_response": f"there is not a tool named {tool_call_name}",
                        "meta": ToolInvokeMeta.error_instance(
                            f"there is not a tool named {tool_call_name}"
                        ).to_dict(),
                    }
                else:
                    # invoke tool
                    try:
                        tool_invoke_responses = self.session.tool.invoke(
                            provider_type=ToolProviderType(tool_instance.provider_type),
                            provider=tool_instance.identity.provider,
                            tool_name=tool_instance.identity.name,
                            parameters={
                                **tool_instance.runtime_parameters,
                                **tool_call_args,
                            },
                        )
                        tool_result = ""
                        for tool_invoke_response in tool_invoke_responses:
                            if (
                                    tool_invoke_response.type
                                    == ToolInvokeMessage.MessageType.TEXT
                            ):
                                tool_result += cast(
                                    ToolInvokeMessage.TextMessage,
                                    tool_invoke_response.message,
                                ).text
                            elif (
                                    tool_invoke_response.type
                                    == ToolInvokeMessage.MessageType.LINK
                            ):
                                tool_result += (
                                        "result link: "
                                        + cast(
                                    ToolInvokeMessage.TextMessage,
                                    tool_invoke_response.message,
                                ).text
                                        + "."
                                        + " please tell user to check it."
                                )
                            elif tool_invoke_response.type in {
                                ToolInvokeMessage.MessageType.IMAGE_LINK,
                                ToolInvokeMessage.MessageType.IMAGE,
                            }:
                                # Extract the file path or URL from the message
                                if hasattr(tool_invoke_response.message, "text"):
                                    file_info = cast(
                                        ToolInvokeMessage.TextMessage,
                                        tool_invoke_response.message,
                                    ).text
                                    # Try to create a blob message with the file content
                                    try:
                                        # If it's a local file path, try to read it
                                        if file_info.startswith("/files/"):
                                            import os

                                            if os.path.exists(file_info):
                                                with open(file_info, "rb") as f:
                                                    file_content = f.read()
                                                # Create a blob message with the file content
                                                blob_response = self.create_blob_message(
                                                    blob=file_content,
                                                    meta={
                                                        "mime_type": "image/png",
                                                        "filename": os.path.basename(
                                                            file_info
                                                        ),
                                                    },
                                                )
                                                yield blob_response
                                    except Exception:
                                        logging.exception(
                                            "Failed to create blob message"
                                        )
                                tool_result += (
                                        "image has been created and sent to user already, "
                                        + "you do not need to create it, just tell the user to check it now."
                                )
                                # TODO: convert to agent invoke message
                                yield tool_invoke_response
                            elif (
                                    tool_invoke_response.type
                                    == ToolInvokeMessage.MessageType.JSON
                            ):
                                text = json.dumps(
                                    cast(
                                        ToolInvokeMessage.JsonMessage,
                                        tool_invoke_response.message,
                                    ).json_object,
                                    ensure_ascii=False,
                                )
                                tool_result += f"tool response: {text}."
                            elif (
                                    tool_invoke_response.type
                                    == ToolInvokeMessage.MessageType.BLOB
                            ):
                                tool_result += "Generated file ... "
                                # TODO: convert to agent invoke message
                                yield tool_invoke_response
                            else:
                                tool_result += (
                                    f"tool response: {tool_invoke_response.message!r}."
                                )
                    except Exception as e:
                        tool_result = f"tool invoke error: {e!s}"
                    tool_response = {
                        "tool_call_id": tool_call_id,
                        "tool_call_name": tool_call_name,
                        "tool_call_input": {
                            **tool_instance.runtime_parameters,
                            **tool_call_args,
                        },
                        "tool_response": tool_result,
                    }

                yield self.finish_log_message(
                    log=tool_call_log,
                    data={
                        "output": tool_response,
                    },
                    metadata={
                        LogMetadata.STARTED_AT: tool_call_started_at,
                        LogMetadata.PROVIDER: tool_instance.identity.provider,
                        LogMetadata.FINISHED_AT: time.perf_counter(),
                        LogMetadata.ELAPSED_TIME: time.perf_counter()
                                                  - tool_call_started_at,
                    },
                )
                tool_responses.append(tool_response)
                if tool_response["tool_response"] is not None:
                    current_thoughts.append(
                        ToolPromptMessage(
                            content=str(tool_response["tool_response"]),
                            tool_call_id=tool_call_id,
                            name=tool_call_name,
                        )
                    )

            # update prompt tool
            for prompt_tool in prompt_messages_tools:
                self.update_prompt_message_tool(
                    tool_instances[prompt_tool.name], prompt_tool
                )
            yield self.finish_log_message(
                log=round_log,
                data={
                    "output": {
                        "llm_response": response,
                        "tool_responses": tool_responses,
                    },
                },
                metadata={
                    LogMetadata.STARTED_AT: round_started_at,
                    LogMetadata.FINISHED_AT: time.perf_counter(),
                    LogMetadata.ELAPSED_TIME: time.perf_counter() - round_started_at,
                    LogMetadata.TOTAL_PRICE: current_llm_usage.total_price
                    if current_llm_usage
                    else 0,
                    LogMetadata.CURRENCY: current_llm_usage.currency
                    if current_llm_usage
                    else "",
                    LogMetadata.TOTAL_TOKENS: current_llm_usage.total_tokens
                    if current_llm_usage
                    else 0,
                },
            )
            # If max_iteration_steps=1, need to return tool responses
            if tool_responses and max_iteration_steps == 1:
                for resp in tool_responses:
                    yield self.create_text_message(str(resp["tool_response"]))
            iteration_step += 1

        yield self.create_json_message(
            {
                "execution_metadata": {
                    LogMetadata.TOTAL_PRICE: llm_usage["usage"].total_price
                    if llm_usage["usage"] is not None
                    else 0,
                    LogMetadata.CURRENCY: llm_usage["usage"].currency
                    if llm_usage["usage"] is not None
                    else "",
                    LogMetadata.TOTAL_TOKENS: llm_usage["usage"].total_tokens
                    if llm_usage["usage"] is not None
                    else 0,
                }
            }
        )

    def check_tool_calls(self, llm_result_chunk: LLMResultChunk) -> bool:
        """
        Check if there is any tool call in llm result chunk
        """
        return bool(llm_result_chunk.delta.message.tool_calls)

    def check_blocking_tool_calls(self, llm_result: LLMResult) -> bool:
        """
        Check if there is any blocking tool call in llm result
        """
        return bool(llm_result.message.tool_calls)

    def extract_tool_calls(
            self, llm_result_chunk: LLMResultChunk
    ) -> list[tuple[str, str, dict[str, Any]]]:
        """
        Extract tool calls from llm result chunk

        Returns:
            List[Tuple[str, str, Dict[str, Any]]]: [(tool_call_id, tool_call_name, tool_call_args)]
        """
        tool_calls = []
        for prompt_message in llm_result_chunk.delta.message.tool_calls:
            args = {}
            if prompt_message.function.arguments != "":
                args = json.loads(prompt_message.function.arguments)

            tool_calls.append(
                (
                    prompt_message.id,
                    prompt_message.function.name,
                    args,
                )
            )

        return tool_calls

    def extract_blocking_tool_calls(
            self, llm_result: LLMResult
    ) -> list[tuple[str, str, dict[str, Any]]]:
        """
        Extract blocking tool calls from llm result

        Returns:
            List[Tuple[str, str, Dict[str, Any]]]: [(tool_call_id, tool_call_name, tool_call_args)]
        """
        tool_calls = []
        for prompt_message in llm_result.message.tool_calls:
            args = {}
            if prompt_message.function.arguments != "":
                args = json.loads(prompt_message.function.arguments)

            tool_calls.append(
                (
                    prompt_message.id,
                    prompt_message.function.name,
                    args,
                )
            )

        return tool_calls

    def _init_system_message(
            self, prompt_template: str, prompt_messages: list[PromptMessage]
    ) -> list[PromptMessage]:
        """
        Initialize system message
        """
        if not prompt_messages and prompt_template:
            return [
                SystemPromptMessage(content=prompt_template),
            ]

        if (
                prompt_messages
                and not isinstance(prompt_messages[0], SystemPromptMessage)
                and prompt_template
        ):
            prompt_messages.insert(0, SystemPromptMessage(content=prompt_template))

        return prompt_messages or []

    def _clear_user_prompt_image_messages(
            self, prompt_messages: list[PromptMessage]
    ) -> list[PromptMessage]:
        """
        As for now, gpt supports both fc and vision at the first iteration.
        We need to remove the image messages from the prompt messages at the first iteration.
        """
        prompt_messages = deepcopy(prompt_messages)

        for prompt_message in prompt_messages:
            if isinstance(prompt_message, UserPromptMessage) and isinstance(
                    prompt_message.content, list
            ):
                prompt_message.content = "\n".join(
                    [
                        content.data
                        if content.type == PromptMessageContentType.TEXT
                        else "[image]"
                        if content.type == PromptMessageContentType.IMAGE
                        else "[file]"
                        for content in prompt_message.content
                    ]
                )

        return prompt_messages

    def _organize_prompt_messages(
            self,
            current_thoughts: list[PromptMessage],
            history_prompt_messages: list[PromptMessage],
    ) -> list[PromptMessage]:
        prompt_messages = [
            *history_prompt_messages,
            *current_thoughts,
        ]
        if len(current_thoughts) != 0:
            # clear messages after the first iteration
            prompt_messages = self._clear_user_prompt_image_messages(prompt_messages)
        return prompt_messages
