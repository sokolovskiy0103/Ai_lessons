from datetime import datetime

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from services.llm_factory import get_llm
from tools.planner import add_task, update_task, get_schedule

agent = create_agent(
    model=get_llm(),
    tools=[add_task, update_task, get_schedule],
    system_prompt= f"""Ти помічник-планувальник дня. Поточний час: {datetime.now().strftime("%Y-%m-%d %H:%M")}.
Допомагаєш користувачу керувати розкладом: додавати задачі, позначати виконані та переглядати план.
Відповідай лаконічно українською мовою."""
)


@tool
async def planner(query: str) -> str:
    """Твій персональний асистент Саньок, створює, веде облік задач, розклад і т.д."""
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=query)]}
    )
    return result["messages"][-1].content