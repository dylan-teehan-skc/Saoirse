import random
from openai import OpenAI
from typing import List, Dict, Tuple
from Agent import Agent


client = OpenAI(api_key='sk-pDpvt5Anv-ZWkK_c-4HoMhw0uLpWC-GIxqBjwuPZU7T3BlbkFJROPxPbQUxJlm1nt4I0SRIWpskDJHesKNy-SxnwR0sA')



class Negotiator:
    def __init__(self, agents: List[Agent]):
        self.agents = agents

    def negotiate(self, topic: str, max_rounds: int = 5) -> Tuple[str, Dict[str, float]]:
        context = f"The topic of negotiation is: {topic}"
        current_proposal = ""
        
        for round in range(max_rounds):
            print(f"\nRound {round + 1}")
            for agent in self.agents:
                if round == 0:
                    response = agent.generate_proposal(context)
                else:
                    response = agent.respond_to_proposal(current_proposal, context)
                print(f"{agent.name} ({agent.role}): {response}\n")
                current_proposal = response
                context += f"\n{agent.name}'s response: {response}"

            if self.check_agreement(response):
                print("Agreement reached!")
                return self.summarize_agreement(context)

        return self.find_compromise(context)

    def check_agreement(self, response: str) -> bool:
        agreement_phrases = ["agree", "accept", "that works", "let's do that"]
        return any(phrase in response.lower() for phrase in agreement_phrases)

    def summarize_agreement(self, context: str) -> Tuple[str, Dict[str, float]]:
        prompt = f"""
        Given the negotiation context:
        {context}

        The agents have reached an agreement. Summarize the final decision, clearly stating the agreed-upon vacation destination and any key points of the agreement.
        Ensure the summary is consistent with all agents' roles, goals, and initial conditions.
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant summarizing a negotiation outcome."},
                {"role": "user", "content": prompt}
            ]
        )
        final_decision = response.choices[0].message.content
        satisfaction_scores = self.calculate_satisfaction_scores(final_decision)
        return final_decision, satisfaction_scores

    def find_compromise(self, context: str) -> Tuple[str, Dict[str, float]]:
        prompt = f"""
        Given the negotiation context:
        {context}

        The agents couldn't reach a full agreement. Analyze their positions, roles, and goals to suggest a fair compromise.
        Provide a clear, specific decision on the vacation spot.
        Ensure the compromise is consistent with all agents' roles, goals, and initial conditions as much as possible.
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant expert in conflict resolution."},
                {"role": "user", "content": prompt}
            ]
        )
        compromise = response.choices[0].message.content
        satisfaction_scores = self.calculate_satisfaction_scores(compromise)
        return compromise, satisfaction_scores

    def calculate_satisfaction_scores(self, final_decision: str) -> Dict[str, float]:
        satisfaction_scores = {}
        for agent in self.agents:
            score, explanation = agent.calculate_satisfaction(final_decision)
            satisfaction_scores[agent.name] = score
            print(f"{agent.name}'s satisfaction: {score:.2f}")
            print(f"Explanation: {explanation}\n")
        return satisfaction_scores

def get_user_input() -> tuple:
    topic = input("Enter the negotiation topic: ")
    num_agents = int(input("Enter the number of agents (2 or more): "))
    agents = []

    for i in range(num_agents):
        name = input(f"Enter name for Agent {i+1}: ")
        role = input(f"Enter role for {name}: ")
        goal = input(f"Enter goal for {name}: ")
        verbose = input(f"Enter verbose description for {name}: ")
        conditions = []
        while True:
            condition = input(f"Enter a condition for {name} (or press Enter to finish): ")
            if condition == "":
                break
            conditions.append(condition)
        agents.append(Agent(name, role, goal, verbose, conditions))

    return topic, agents

def main():
    topic, agents = get_user_input()

    negotiator = Negotiator(agents)
    final_decision, satisfaction_scores = negotiator.negotiate(topic)

    print("\nFinal Decision:")
    print(final_decision)

    print("\nSatisfaction Scores:")
    for agent, score in satisfaction_scores.items():
        print(f"{agent}: {score:.2f}")

if __name__ == "__main__":
    main()