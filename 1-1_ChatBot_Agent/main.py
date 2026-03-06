import os
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage,HumanMessage
from langgraph.graph import StateGraph,START,END
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes,filters
from env import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

class AgentState(TypedDict): #typeddict는 딕셔너리의 키와 값의 타입이 명확하게 정의 할 떄 사용 즉, 정의 해둔 타입과 다르게 값이 들어오면 에러가 발생한다. 실행하면 오류 없이 일반 딕셔너리 처럼 작동한다.
    user_query: str
    messages: list

def create_workflow():
    """ 구조
    START -> analyze_query -> generate_response -> END
    """

    # 1. LLM (모델 정의)
    model = ChatOpenAI(model="gpt-4o-mini")

    # 2. 각 노드 함수들 정의(각 노드는 state를 입력 받아 업데이트 된 state를 반환)
    def analyze_query_node(state: AgentState) -> AgentState: #state를 받고 업데이트 된 state를 반환
        user_query = state["user_query"]

        #system_msg를 그냥 넘겨도 되지만 랭그래프의 규칙에서는 SystemMessage 클래스로 받아서 넘겨야 한다.
        system_message = SystemMessage(content = """
            당신은 전문 AI 어시스턴트 입니다.
            사용자의 질문에 대해 정확하고 친절한 한국어 답변을 제공하세요.
        """)

        return {
            #messages가 리스트인 이유는 응답을 생성할때 필요한 state 형태 구조가 리스트 구조로 될거고
            #거기서 system_msg를 먼저 받고 그 후에 Human_msg 받을 것이기 때문에 리스트 형태로 만들어야 한다.
            "messages" : [system_message,HumanMessage(content=user_query)],
            "user_query":user_query
        }

    def generate_response_node(state: AgentState) -> AgentState:
        messages = state["messages"]
        response = model.invoke(messages) #모델 호출
        return {
            "messages" : [response],
            "user_query": state["user_query"]
        }

    # 3. 그래프 생성 및 구성
    workflow = StateGraph(AgentState)

    # 4. 노드 추가
    workflow.add_node("analyze_query_node", analyze_query_node)
    workflow.add_node("generate_response_node", generate_response_node)

    # 5. 엣지 추가
    workflow.add_edge(START, "analyze_query_node")
    workflow.add_edge("analyze_query_node", "generate_response_node")
    workflow.add_edge("generate_response_node", END)

    # 6. 그래프 컴파일
    return workflow.compile()

class ChatBot():
    def __init__(self):
        self.workflow = create_workflow() #그래프 생성 및 컴파일

    def process_message(self, user_message : str) -> str:
        initial_state : AgentState = {
            "user_query": user_message,
            "messages": []
        }
        result = self.workflow.invoke(initial_state) #그래프 실행

        messages = result["messages"]
        print(messages)
        print("------------------")
        print(messages[0])
        print("------------------")
        print(messages[0].content)
        print(result)

        return "..."

async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.text is None:
        return
    user_message = update.message.text

    result = ChatBot().process_message(user_message)

    await update.message.reply_text(result)

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT,handler))

app.run_polling()
