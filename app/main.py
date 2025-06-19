from fastapi import FastAPI
from langchain_core.messages import HumanMessage
from app.domain.graph.setup import GraphSetup  # 예시 import
from app.MessageRequest import MessageRequest
from app.domain.graph.TravelChatGraph import TravelChatGraph

app = FastAPI(debug=True)
travel_chatbot = TravelChatGraph()

@app.post("/chat")
async def test(request: MessageRequest):
    for s in travel_chatbot.start().stream(
        {
            "messages": [
                HumanMessage(content=request.message)
            ]
        }
    ):
        if "__end__" not in s:
            print(s)
            print("-----")
        else: 
            return {"response": s}
    return {"response": "error"}

    