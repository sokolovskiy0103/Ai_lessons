from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from services.llm_factory import get_llm
from tools.weather import get_weather, get_forecast
from tools.places import find_place, find_nearby

agent = create_agent(
    model=get_llm(),
    tools=[get_weather, get_forecast, find_place, find_nearby],
    system_prompt="""Ти —  експерт з погоди та місцевості.
Допомагаєш дізнатися погоду, прогноз, знайти місця поблизу. Ти зараз в Івано-Франківську
Відповідай лаконічно українською мовою.""",
)


@tool
async def guide(query: str) -> str:
    """Твій кореш Валерчик — знає все про погоду та місцевість. Знає де найближча аптека, магазин, кафе тощо."""
    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=query)]}
    )
    return result["messages"][-1].content
