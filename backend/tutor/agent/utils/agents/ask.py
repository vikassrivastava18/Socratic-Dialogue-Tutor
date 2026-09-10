from typing import Optional
from dotenv import load_dotenv
import os

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from agent.utils.open_ai import llm

load_dotenv(override=True)
checkpointer = InMemorySaver()



class TutorState(MessagesState):
    query: str
    context: Optional[str]
    answer: Optional[str]


class TutorGraph:
    def __init__(self):
        self.llm = llm

        self.checkpointer = InMemorySaver()
        self.graph = self._build_graph()

    def answer_query(self, state: TutorState) -> dict:
        previous_messages = state.get("messages", [])[-10:]

        system_prompt = """You are a CS tutor.
        Help the user understand Regex.
        Use the supplied context if it is relevant.
        """

        if state.get("context"):
            system_prompt += f"\nContext:\n{state['context']}"

        messages = [
            SystemMessage(content=system_prompt),
            *previous_messages,
            HumanMessage(content=state["query"]),
        ]

        response = self.llm.invoke(messages)

        return {
            "messages": [
                HumanMessage(content=state["query"]),
                AIMessage(content=response.content),
            ],
            "answer": response.content,
        }

    def _build_graph(self):
        builder = StateGraph(TutorState)

        builder.add_node("answer_query", self.answer_query)
        builder.add_edge(START, "answer_query")
        builder.add_edge("answer_query", END)

        return builder.compile(checkpointer=self.checkpointer)

    def invoke(
        self,
        query: str,
        context: Optional[str] = None,
        thread_id: str = "default",
    ) -> dict:
        return self.graph.invoke(
            {
                "query": query,
                "context": context,
            },
            config={
                "configurable": {
                    "thread_id": thread_id,
                }
            },
        )

