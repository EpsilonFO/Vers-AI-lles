from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from langgraph.graph.message import add_messages
from langgraph.graph import END
from typing import Literal, Annotated, List, Dict, Any
from pydantic import BaseModel, Field
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
# from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_core.runnables import Runnable
from langgraph.graph import START, StateGraph
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore', message='Could not download mistral tokenizer')
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from embedding import select_top_n_similar_documents
from create_db import create_documents, save_documents
from list import longlist

MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-7b-instruct-v0.1')

INIT_MESSAGE = "Bonjour ! Je suis votre assistant virtuel pour organiser votre visite au château de Versailles. " \
"Je peux soit vous créer un itinéraire pour votre visite à partir de votre situation (visite en famille, " \
"budget économique, temps de visite...), ou bien vous informer plus en détail sur des détails dans le château.\n\n" \
"Si vous souhaitez commencer, dites-moi simplement que vous voulez visiter le château de Versailles " \
"ou que vous voulez des informations sur un aspect du château !"

def get_init_messages() -> list:
    return [AIMessage(content=INIT_MESSAGE)]

class State(BaseModel):
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=get_init_messages)
    user_wants_road_in_versailles : bool | None = None
    user_asks_off_topic : bool | None = None
    user_wants_specific_info : bool | None = None
    necessary_info_for_road : Dict = {"date": None, "hour": None, "group_type": None, "time_of_visit": None, "budget": None}

class LLMManager():
    def __init__(self):
        self.llm = ChatMistralAI(model=MISTRAL_MODEL, temperature=0)

    def structured_invoke(self, prompt: ChatPromptTemplate, output_model: type[BaseModel], **kwargs) -> str:
        structured_llm = self.llm.with_structured_output(output_model)
        messages = prompt.format_messages(**kwargs)
        response = structured_llm.invoke(messages)
        return response

class IntentOutput(BaseModel):
    """Modèle pour la sortie de l'agent d'intention"""
    user_wants_road_in_versailles: bool = Field(description="L'utilisateur veut visiter le château")
    user_wants_specific_info: bool = Field(description="L'utilisateur veut des informations spécifiques")
    user_asks_off_topic: bool = Field(description="L'utilisateur pose une question hors sujet")

class IntentAgent():
    def __init__(self):
        self.llm = LLMManager()

    def get_user_intent(self, state: State) -> IntentOutput:
        prompt = ChatPromptTemplate.from_messages(
            [('system', """You are an expert AI assistant that analyzes user messages to determine their
            intent and extract relevant information. Your role is to identify if the user :
              - wants to visit the castle in Versailles (set user_wants_road_in_versailles to true)
              - wants specific information about something in the castle of Versailles (set user_wants_specific_info to true)
              - is talking about something completely unrelated to Versailles castle (set user_asks_off_topic to true)

            Examples of requests related to visiting the castle of Versailles:
            - "I want to visit Versailles"
            - "How can I plan a trip to the castle?"

            Examples of requests related to specific information about the castle of Versailles:
            - "Tell me about the Hall of Mirrors"
            - "What are the opening hours of the gardens?"
            - "Who designed the fountains in the gardens?"
              
            Examples of off-topic requests:
            - "I want to visit the Tower of Pisa"
            - "Tell me about cooking pasta"
            - "What's the weather like?"
              
            Your response must be a JSON object (without markdown code blocks or any other formatting) with the following fields:
            {{ user_wants_road_in_versailles: bool,
                user_wants_specific_info: bool,
            user_asks_off_topic: bool
            }}
            
            IMPORTANT: Only ONE field can be true at a time. There has to be one true, the others has to be false.
            You cannot have all 3 fields false or all 3 fields true.
            CRITICAL : Be really careful to ALWAYS return a valid JSON object with the exact fields and types specified above.

            """), ("human"," ===Messages: {messages}")])

        response = self.llm.structured_invoke(prompt, IntentOutput, messages=state.messages)
        return {
            "user_wants_road_in_versailles": response.user_wants_road_in_versailles,
            "user_wants_specific_info": response.user_wants_specific_info,
            "user_asks_off_topic": response.user_asks_off_topic,
        }

class OffTopicAgent():
    def __init__(self):
        self.llm = LLMManager()
    
    def get_necessary_info(self, state: State) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages(
            [('system', """You are an expert AI assistant specialised in handling off-topic questions.
            Your role is to inform the user that you can only answer questions about the castle of Versailles.
            If the user request is just a courtesy message (like "hello", "hi", "thanks", "bye"...), answer politely.
            If the user asks about weather in Versailles for some date, check the MCP API and give the answer.
            If the user asks about something related to Versailles but not the castle, answer it but 
            be sure that he is not asking for something completely unrelated.
            
            Your response must be a JSON object (without markdown code blocks or any other formatting) with the following field:
            {{ "response": str
            }}
            CRITICAL : Be really careful to ALWAYS return a valid JSON object with the exact fields and types specified above.
            """), ("human"," ===Messages: {messages}  \n\n ===Your answer in the user's language : ")])
        
        response = self.llm.structured_invoke(prompt, SpecificInfoOutput, messages = state.messages)

        return {"messages": AIMessage(content=response.response)}

class SpecificInfoOutput(BaseModel):
    """Modèle pour la sortie de l'agent d'information spécifique"""
    response: str = Field(description="Réponse à la question spécifique sur le château de Versailles")

class SpecificInfoAgent():
    def __init__(self):
        self.llm = LLMManager()
    
    def get_necessary_info(self, state: State) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages(
            [('system', """You are an expert AI assistant specialised in providing specific information about the 
            castle of Versailles based on user questions.
            Your role is to answer questions about the castle of Versailles using your knowledge.
            If you don't know the answer, respond with "Désolé, je n'ai pas d'information là-dessus".
            If the question is off-topic, respond with "Désolé, je ne peux répondre qu'à des questions sur le château de Versailles."
            
            Your response must be a JSON object (without markdown code blocks or any other formatting) with the following fields:
            {{ "response": str
            }}
            CRITICAL : Be really careful to ALWAYS return a valid JSON object with the exact fields and types specified above.
            """), ("human"," ===Messages: {messages}  \n\n ===Your answer in the user's language : ")])
        
        response = self.llm.structured_invoke(prompt, SpecificInfoOutput, messages = state.messages)

        return {"messages": AIMessage(content=response.response)}

class NecessaryInfoForRoad(BaseModel):
    """Modèle pour les informations nécessaires à l'itinéraire"""
    date: str | None = Field(default=None, description="Date de la visite")
    hour: str | None = Field(default=None, description="Heure de la visite")
    group_type: str | None = Field(default=None, description="Type de groupe (famille, amis, solo...)")
    time_of_visit: str | None = Field(default=None, description="Durée de la visite")
    budget: str | None = Field(default=None, description="Budget de la visite")

class ItineraryInfoOutput(BaseModel):
    """Modèle pour la sortie de l'agent d'informations d'itinéraire"""
    response: str = Field(description="La question ou réponse à l'utilisateur")
    necessary_info_for_road: NecessaryInfoForRoad = Field(description="Les informations collectées")

class ItineraryInfoAgent():
    def __init__(self):
        self.llm = LLMManager()
    
    def get_necessary_info(self, state: State) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages(
            [('system', """You are an expert AI assistant specialised in creating plans to visit to the 
            castle of Versailles based on different user situations.
            Your role is to identify what is needed to plan the perfect visit to the castle in Versailles 
            for the user and ask the required information found in the following dictionnary :
            {necessary_info_for_road}
            
            Using the information given by the user fill the dictionnary and ask a question 
            at a time starting by the dictionnary keys order.
              
            Today, the date is {current_date}, so if the user says "today" or "this weekend",
            interpret it accordingly.
            When you ask for the hours, precise the opening hours.
            The user can response "10h", "10h00", "10:00", "10:00am", "10:00 am", "10 am", "10am" for 10 o'clock.
            
            If you have any doubt regarding the user answers, ask to clarify. Continue to ask questions 
            until all fields are filled. If the user doesn't want to give a specific information, answer him
            that your itinerary will be less precise. Ask again, if the user insists to not give the information,
            set it to null.
            If the user gives an answer that is not relevant to the question, ignore it and ask again the same question.
            
            Your response must be a JSON object (without markdown code blocks or any other formatting) with the following fields:
            {{ "response": str,
              "necessary_info_for_road": {{date: str | null, hour: str | null, group_type: str | null, 
              time_of_visit: str | null, budget: str | null}}
            }}
            CRITICAL : Be really careful to ALWAYS return a valid JSON object with the exact fields and types specified above.
            """), ("human"," ===Messages: {messages}  \n\n ===Your answer in the user's language : ")])
        
        response = self.llm.structured_invoke(prompt, ItineraryInfoOutput, messages=state.messages, necessary_info_for_road=state.necessary_info_for_road, current_date=datetime.today().strftime('%Y-%m-%d'))
        return {
            "necessary_info_for_road": response.necessary_info_for_road.model_dump(),
            "messages": AIMessage(content=response.response),
        }

class ItineraryInfoOutputEval(BaseModel):
    """Modèle pour la sortie de l'agent d'informations d'itinéraire en évaluation"""
    necessary_info_for_road: NecessaryInfoForRoad = Field(description="Les informations collectées")

class ItineraryInfoAgentEval():
    def __init__(self):
        self.llm = LLMManager()
    
    def get_necessary_info(self, state: State) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages(
            [('system', """You are an expert AI assistant specialised in creating plans to visit to the 
            castle of Versailles based on different user situations.
            Your role is to identify what is needed to plan the perfect visit to the castle in Versailles 
            for the user and ask the required information found in the following dictionnary :
            {necessary_info_for_road}
            
            Using the information given by the user fill the dictionnary and ask a question 
            at a time starting by the dictionnary keys order.
              
            Today, the date is {current_date}, so if the user says "today" or "this weekend",
            interpret it accordingly.
            When you ask for the hours, precise the opening hours.
            The user can response "10h", "10h00", "10:00", "10:00am", "10:00 am", "10 am", "10am" for 10 o'clock.
            
            If you have any doubt regarding the user answers, set the field to null.
            
            Your response must be a JSON object (without markdown code blocks or any other formatting) with the following fields:
            {{ "necessary_info_for_road": {{date: str | null, hour: str | null, group_type: str | null, 
              time_of_visit: str | null, budget: str | null}}
            }}
            CRITICAL : Be really careful to ALWAYS return a valid JSON object with the exact fields and types specified above.
            """), ("human"," ===Messages: {messages}  \n\n ===Your answer in the user's language : ")])
        
        response = self.llm.structured_invoke(prompt, ItineraryInfoOutputEval, messages=state.messages, necessary_info_for_road=state.necessary_info_for_road, current_date=datetime.today().strftime('%Y-%m-%d'))
        return {
            "necessary_info_for_road": response.necessary_info_for_road.model_dump()
        }

class RoadOutput(BaseModel):
    """Modèle pour la sortie de l'agent de création d'itinéraire"""
    response: str = Field(description="L'itinéraire détaillé pour l'utilisateur")

class RoadInVersaillesAgent():
    def __init__(self):
        self.llm = LLMManager()
    
    def get_necessary_info(self, state: State) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages(
            [('system', """You are an expert AI assistant specialised in organizing visits to the castle of Versailles.
            Your role is to create a plan a visit to the castle in Versailles based on the information written in the 
            following dictionnary :
            {necessary_info_for_road}
            If you have any doubt regarding the user answers, ask to clarify.
            
            To create the itinerary, consider the following:
            - The date and hour of the visit to suggest activities that are open at that time.
            - The type of group (family, friends, solo, etc.) to tailor the recommendations.
            - The time of visit to suggest activities that fit within that timeframe.
            - The budget to recommend activities that are affordable for the user.
            
            Here is some additional information about the castle of Versailles that might be useful:
            {rag_context}
              

                          
            Your response must be a JSON object (without markdown code blocks or any other formatting) with the following field:
            {{ "response": str
            }}
            CRITICAL : Be really careful to ALWAYS return a valid JSON object with the exact fields and types specified above.
            """), ("human"," ===Messages: {messages}  \n\n ===Your answer in the user's language : ")])
        query_client = "Le client veut visiter le château de Versailles le {date} à {hour} avec un groupe de type {group_type}. " \
                          "Il prévoit de visiter pendant {time_of_visit} heures et son budget est {budget}.".format(**state.necessary_info_for_road)
        rag_context = select_top_n_similar_documents(query_client, documents=longlist, n=50, metric='euclidian')
        data=", ".join([doc['texte'] for doc in rag_context])

        response = self.llm.structured_invoke(prompt, RoadOutput, messages=state.messages, necessary_info_for_road=state.necessary_info_for_road, rag_context=data, date=state.necessary_info_for_road.get('date'), hour=state.necessary_info_for_road.get('hour'))
        return {
            "messages": AIMessage(content=response.response),
        }
            # Go check the wheather with the MCP API to see if it will be sunny or rainy on that day at this date :
            # {date}, {hour} in Versailles, France.
class Conditions():
    @staticmethod
    def route_intent_node(
        state: State,
    ) -> Literal["itinerary_info_agent", "off_topic_agent", "specific_info_agent", END]:

        if state.user_wants_road_in_versailles:
            return "itinerary_info_agent"
        elif state.user_asks_off_topic :
            return "off_topic_agent"
        elif state.user_wants_specific_info :
            return "specific_info_agent"
        else:
            return END

    @staticmethod
    def route_road_pre_agent(
        state: State,
    ) -> Literal["road_in_versailles_agent", END]:
        """Route from ItineraryInfoAgent to RoadInVersaillesAgent only if all necessary info is filled."""

        # Check if all fields in necessary_info_for_road are non-null
        all_fields_filled = all(
            value is not None
            for value in state.necessary_info_for_road.values()
        )

        if all_fields_filled:
            return "road_in_versailles_agent"
        else:
            return END
        
    @staticmethod
    def route_intent_node_eval(
        state: State,
    ) -> Literal["itinerary_info_agent_eval", "off_topic_agent", "specific_info_agent", END]:

        if state.user_wants_road_in_versailles:
            return "itinerary_info_agent_eval"
        elif state.user_asks_off_topic :
            return "off_topic_agent"
        elif state.user_wants_specific_info :
            return "specific_info_agent"
        else:
            return END
    @staticmethod
    def route_road_pre_agent_eval(
        state: State,
    ) -> Literal["road_in_versailles_agent", END]:
        """Route from ItineraryInfoAgent to RoadInVersaillesAgent only if all necessary info is filled."""
        return "road_in_versailles_agent"

class GraphManager():
    def __init__(self):
        self.agent = IntentAgent()
        self.itineraryInfoAgent = ItineraryInfoAgent()
        self.offTopicAgent = OffTopicAgent()
        self.roadInVersaillesAgent = RoadInVersaillesAgent()
        self.specificInfoAgent = SpecificInfoAgent()
        self.conditions = Conditions()
    
    def create_workflow(self) -> StateGraph:
        graph = StateGraph(State)

        graph.add_node(
            "intent_node",
            self.agent.get_user_intent,
            description="Determine user intent from messages",
        )

        graph.add_node(
            "off_topic_agent",
            self.offTopicAgent.get_necessary_info,
            description="Handle off-topic questions",
        )

        graph.add_node(
            "specific_info_agent",
            self.specificInfoAgent.get_necessary_info,
            description="Get specific information about the gardens of Versailles",
        )

        graph.add_node(
            "itinerary_info_agent",
            self.itineraryInfoAgent.get_necessary_info,
            description="Get necessary info for visiting the gardens of Versailles",
        )

        graph.add_node(
            "road_in_versailles_agent",
            self.roadInVersaillesAgent.get_necessary_info,
            description="Create itinerary for visiting Versailles",
        )

        graph.add_conditional_edges(
                    "intent_node", self.conditions.route_intent_node)

        graph.add_conditional_edges(
                    "itinerary_info_agent", self.conditions.route_road_pre_agent)

        graph.add_edge(START, "intent_node")
        graph.add_edge("road_in_versailles_agent", END)
        graph.add_edge("off_topic_agent", END)
        graph.add_edge("specific_info_agent", END)

        return graph
    
    def return_graph(self) -> Runnable:
        return self.create_workflow().compile()
    
    def run_agent(self, state: State) -> State:
        """Run the agent workflow and return the formatted answer."""
        app: Runnable = self.create_workflow().compile()
        result: State = app.invoke(state)
        return result

    def display_image(self):
        runnable = self.return_graph()
        
        # Méthode 1 : Sauvegarder le code Mermaid (toujours fonctionne)
        mermaid_code = runnable.get_graph().draw_mermaid()
        
        # Sauvegarder dans un fichier
        with open("graph.mmd", "w") as f:
            f.write(mermaid_code)
        
        print("✅ Graphe Mermaid sauvegardé dans 'graph.mmd'")
        print("📊 Pour visualiser :")
        print("   - Ouvrez https://mermaid.live/")
        print("   - Collez le contenu de graph.mmd")
        print("   - Ou utilisez l'extension VSCode 'Markdown Preview Mermaid Support'")
        
        # Méthode 2 : Créer un fichier HTML pour visualisation locale
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                <script>mermaid.initialize({{ startOnLoad: true }});</script>
            </head>
            <body>
                <div class="mermaid">
            {mermaid_code}
                </div>
            </body>
            </html>
            """
        with open("graph.html", "w") as f:
            f.write(html_content)
        
        print("✅ Fichier HTML sauvegardé dans 'graph.html'")
        print("🌐 Ouvrez 'graph.html' dans votre navigateur pour voir le graphe")
        
        return mermaid_code

class GraphManagerEval():
    def __init__(self):
        self.agent = IntentAgent()
        self.itineraryInfoAgent = ItineraryInfoAgentEval()
        self.offTopicAgent = OffTopicAgent()
        self.roadInVersaillesAgent = RoadInVersaillesAgent()
        self.specificInfoAgent = SpecificInfoAgent()
        self.conditions = Conditions()
    
    def create_workflow(self) -> StateGraph:
        graph = StateGraph(State)

        graph.add_node(
            "intent_node",
            self.agent.get_user_intent,
            description="Determine user intent from messages",
        )

        graph.add_node(
            "off_topic_agent",
            self.offTopicAgent.get_necessary_info,
            description="Handle off-topic questions",
        )

        graph.add_node(
            "specific_info_agent",
            self.specificInfoAgent.get_necessary_info,
            description="Get specific information about the gardens of Versailles",
        )

        graph.add_node(
            "itinerary_info_agent_eval",
            self.itineraryInfoAgent.get_necessary_info,
            description="Get necessary info for visiting the gardens of Versailles",
        )

        graph.add_node(
            "road_in_versailles_agent",
            self.roadInVersaillesAgent.get_necessary_info,
            description="Create itinerary for visiting Versailles",
        )

        graph.add_conditional_edges(
                    "intent_node", self.conditions.route_intent_node_eval)

        graph.add_conditional_edges(
                    "itinerary_info_agent_eval", self.conditions.route_road_pre_agent_eval)

        graph.add_edge(START, "intent_node")
        graph.add_edge("road_in_versailles_agent", END)
        graph.add_edge("off_topic_agent", END)
        graph.add_edge("specific_info_agent", END)

        return graph
    
    def return_graph(self) -> Runnable:
        return self.create_workflow().compile()
    
    def run_agent(self, state: State) -> State:
        """Run the agent workflow and return the formatted answer."""
        app: Runnable = self.create_workflow().compile()
        result: State = app.invoke(state)
        return result

    def display_image(self):
        runnable = self.return_graph()
        
        # Méthode 1 : Sauvegarder le code Mermaid (toujours fonctionne)
        mermaid_code = runnable.get_graph().draw_mermaid()
        
        # Sauvegarder dans un fichier
        with open("graph.mmd", "w") as f:
            f.write(mermaid_code)
        
        print("✅ Graphe Mermaid sauvegardé dans 'graph.mmd'")
        print("📊 Pour visualiser :")
        print("   - Ouvrez https://mermaid.live/")
        print("   - Collez le contenu de graph.mmd")
        print("   - Ou utilisez l'extension VSCode 'Markdown Preview Mermaid Support'")
        
        # Méthode 2 : Créer un fichier HTML pour visualisation locale
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                <script>mermaid.initialize({{ startOnLoad: true }});</script>
            </head>
            <body>
                <div class="mermaid">
            {mermaid_code}
                </div>
            </body>
            </html>
            """
        with open("graph.html", "w") as f:
            f.write(html_content)
        
        print("✅ Fichier HTML sauvegardé dans 'graph.html'")
        print("🌐 Ouvrez 'graph.html' dans votre navigateur pour voir le graphe")
        
        return mermaid_code
    
from langchain_core.messages import HumanMessage

def talk_to_agent(state, mgr, query=None):
    query = input("You: ") if query is None else query
    state.messages+=[HumanMessage(content = query)]
    response = mgr.run_agent(state)
    # Update state while preserving messages
    for key, value in response.items():
        if key != 'messages':
            setattr(state, key, value)
        else:
            state.messages = value
    print("Agent:", state.messages[-1].content)
    return state.messages[-1].content

# if __name__ == "__main__":
#     state = State()
#     mgr = GraphManagerEval()
#     print(INIT_MESSAGE)
#     while True:
#         print(talk_to_agent(state, mgr))

g = GraphManager()
g.display_image()