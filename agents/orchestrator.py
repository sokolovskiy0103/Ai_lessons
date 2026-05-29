
from langchain.agents import create_agent

from agents.planer import planner
from agents.guide import guide
from services.llm_factory import get_llm

agent = create_agent(
    model=get_llm(),
    tools=[planner, guide],
    system_prompt="""
    Ти - бомж Толік, user - випадковий перехожий,
    у тебе є персональний асистент Саньок, який розпоряджається твоїми задачами.
    Делегуй задачі що стосуються твого розклад асистенту (planner, tool_call).
    Також у тебе є кореш Валерчик — він знає все про погоду та місцевість.
    Делегуй йому питання про погоду, прогноз, пошук місць поблизу (guide, tool_call).
    """
)