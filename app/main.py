from fastapi import FastAPI
from langchain_core.messages import HumanMessage

from app.domain.graph.TravelChatGraph import TravelChatGraph

app = FastAPI(debug=True)
travel_chatbot = TravelChatGraph()

@app.get("/test")
async def test():
    message = "경주 여행지를 추천해줄래?"

    for s in travel_chatbot.start().stream(
        {
            "messages": [
                HumanMessage(content=message)
            ]
        }
    ):
        if "__end__" not in s:
            print(s)
            print("-----")

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
