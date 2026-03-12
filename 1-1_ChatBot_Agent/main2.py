# import os
# import logging

# from crewai import Crew,Agent,Task
# from crewai.project import CrewBase,task,agent,crew
# from telegram import Update
# from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes,filters
# from env import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# @CrewBase
# class ChatBotCrew:
#     agents_config = "config/agents.yaml"
#     tasks_config = "config/tasks.yaml"

#     @agent
#     def communication_agent(self) -> Agent:
#         return Agent(config=self.agents_config["communication_agent"], verbose = True) #type: ignore

#     @task
#     def communication_task(self) -> Task:
#         return Task(config=self.tasks_config["communication_task"]) #type: ignore

#     @crew
#     def crew(self) -> Crew:
#         print(self.agents_config)
#         print(self.tasks_config)
#         return Crew(
#             agents=[self.communication_agent()],
#             tasks=[self.communication_task()],
#             verbose = True,
#         )

# async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if update.message is None or update.message.text is None:
#         return
#     user_message = update.message.text

#     chatbot_crew = ChatBotCrew()

#     result = chatbot_crew.crew().kickoff(inputs={"message": user_message}) #input에서 키값은 tasks.yaml의 description에서 {message}로 되어있는 부분과 일치해야한다.
#     print(result)
#     await update.message.reply_text(result.raw)

# app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

# app.add_handler(MessageHandler(filters.TEXT,handler))

# app.run_polling()

import os
from crewai import Crew, Agent, Task
from crewai.project import CrewBase, task, agent, crew
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from env import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


@CrewBase
class ChatBotCrew:

    # agents_config = "config/agents.yaml"
    # tasks_config = "config/tasks.yaml"

    @agent
    def communication_agent(self) -> Agent:
        return Agent(
            role="전문 소통 분석가",
            goal="사용자의 질문을 심층적으로 분석하고, 가장 정확하고 유용한 정보를 찾아내어 전달한다.",
            backstory="""
            당신은 최첨단 AI 기술과 깊이 있는 데이터 분석 능력을 겸비한 전문 정보 분석가입니다.
            어떤 질문이든 그 본질을 파악하고, 웹 검색과 같은 강력한 도구를 활용하여 사용자에게 가장 필요한 맞춤형 답변을 제공하는 것을 사명으로 삼고 있습니다.
            """,
            llm="openai/o4-mini",
            tools=[],
        )

    @task
    def communication_task(self) -> Task:
        return Task(
            agent=self.communication_agent(),
            description="""
            사용자로부터 받은 메시지('{message}')를 단계별로 분석합니다.
            1. 질문의 핵심 키워드와 숨은 의도를 파악합니다.
            2. 필요 시, 웹 검색 도구를 사용하여 관련 최신 정보를 찾습니다.
            3. 수집된 정보를 종합하여 사용자가 이해하기 쉬운 형태로 명확하고 친절한 답변을 생성합니다.
            """,
            expected_output="""
            사용자의 질문 의도에 완벽하게 부합하는, 명확하고 간결하며 친절한 톤의 한국어 답변.
            질문이 정보성 질문의 경우, 핵심 내용을 요약하고 신뢰할 수 있는 출처(URL)를 포함해야 합니다.
            분석 과정이나 단계별 설명 없이, 최종 답변만 출력하세요.
            """,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.communication_agent()],
            tasks=[self.communication_task()],
            verbose=True,
        )


async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.message is None or update.message.text is None:
        return

    user_message = update.message.text

    chatbot_crew = ChatBotCrew()

    result = chatbot_crew.crew().kickoff(inputs={"message": user_message})

    await update.message.reply_text(result.raw)


app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, handler))

app.run_polling()
