def test_agent_general_question():
    from app.agents.react_agent import get_agent

    agent = get_agent()
    result = agent.invoke({"messages": [{"role": "user", "content": "你好，请用一句话介绍你自己"}]})
    assert "messages" in result
    assert len(result["messages"]) > 0