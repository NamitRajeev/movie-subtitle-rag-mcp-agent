from src.agent.schemas import AgentRequest


request = AgentRequest(
    intent="information",
    movie="Avengers.Infinity.War.2018",
    query="What does Thanos want from the Avengers?"
)

print(request)
print(request.model_dump())