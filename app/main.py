from fastapi import FastAPI
from langchain_core.messages import HumanMessage
from app.domain.graph.setup import GraphSetup  # 예시 import
from app.MessageRequest import MessageRequest
from app.domain.graph.TravelChatGraph import TravelChatGraph

app = FastAPI(debug=True)
travel_chatbot = TravelChatGraph()

@app.post("/chat")
async def test(request: MessageRequest):
    messages = []
    final_response = None
    
    for s in travel_chatbot.start().stream(
        {
            "messages": [
                HumanMessage(content=request.message)
            ],
            "agent_scratchpad": []
        }
    ):
        # 각 노드의 메시지 수집
        for key, value in s.items():
            if key != "__end__" and isinstance(value, dict) and "messages" in value:
                messages.extend(value["messages"])
        
        # 최종 결과 확인
        if "__end__" in s:
            final_response = s["__end__"]
            break
        elif "supervisor" in s and s["supervisor"].get("next") == "FINISH":
            # supervisor가 FINISH를 반환한 경우, 수집된 메시지에서 응답 추출
            if messages:
                # 마지막 메시지의 내용을 반환
                final_response = messages[-1].content
            else:
                final_response = "대화가 완료되었습니다."
            break
    
    if final_response:
        return {"response": final_response}
    else:
        return {"response": "처리 중 오류가 발생했습니다."}

    