import random
from openai import OpenAI
from typing import List, Dict


client = OpenAI(api_key='sk-pDpvt5Anv-ZWkK_c-4HoMhw0uLpWC-GIxqBjwuPZU7T3BlbkFJROPxPbQUxJlm1nt4I0SRIWpskDJHesKNy-SxnwR0sA')

class Agent:
    def __init__(self, name: str, role: str, goal: str, verbose: str, conditions: List[str]):
        self.name = name
        self.role = role
        self.goal = goal
        self.verbose = verbose
        self.conditions = conditions
        self.satisfaction = 0
        self.previous_proposals = []

    def generate_proposal(self, context: str) -> str:
        prompt = f"""
        You are {self.name}, a {self.role} with the following goal: {self.goal}
        Your verbose description: {self.verbose}
        Your conditions are: {', '.join(self.conditions)}

        Your previous proposals and responses:
        {' '.join(self.previous_proposals)}

        Given the current context of the negotiation:
        {context}

        Generate a concise proposal for a vacation spot. Be specific about the location and explain why it meets your conditions and aligns with your role and goal.
        Maintain consistency with your role, goal, verbose description, and previous statements.
        Do not agree to proposals that contradict your core conditions or goal.
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant roleplaying as a negotiator with a specific role and goal. Maintain consistent preferences and do not contradict your initial conditions or goal."},
                {"role": "user", "content": prompt}
            ]
        )
        proposal = response.choices[0].message.content
        self.previous_proposals.append(proposal)
        return proposal

    def respond_to_proposal(self, proposal: str, context: str) -> str:
        prompt = f"""
        You are {self.name}, a {self.role} with the following goal: {self.goal}
        Your verbose description: {self.verbose}
        Your conditions are: {', '.join(self.conditions)}

        Your previous proposals and responses:
        {' '.join(self.previous_proposals)}

        Current proposal:
        {proposal}

        Context of the negotiation:
        {context}

        Respond to this proposal. If you agree, say so only if it aligns with your core conditions and goal.
        If not, explain why and make a counter-proposal or suggest a compromise.
        Be concise and specific about locations.
        Maintain consistency with your role, goal, verbose description, and previous statements.
        Do not agree to proposals that contradict your core conditions or goal.
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant roleplaying as a negotiator with a specific role and goal. Maintain consistent preferences and do not contradict your initial conditions or goal."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content
        self.previous_proposals.append(reply)
        return reply

    def calculate_satisfaction(self, final_decision: str) -> float:
        prompt = f"""
        You are {self.name}, a {self.role} with the following goal: {self.goal}
        Your verbose description: {self.verbose}
        Your conditions are: {', '.join(self.conditions)}

        The final decision of the negotiation is:
        {final_decision}

        Based on your role, goal, and conditions, calculate your satisfaction with this outcome on a scale of 0 to 1, where:
        0 = Completely unsatisfied
        0.5 = Neutral
        1 = Completely satisfied

        Provide the satisfaction score as a float between 0 and 1, followed by a brief explanation for your rating.
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant calculating satisfaction based on negotiation outcomes."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content
        try:
            satisfaction_score = float(result.split('\n')[0])
            explanation = '\n'.join(result.split('\n')[1:])
        except ValueError:
            # If conversion fails, assign a default score and use the entire response as explanation
            satisfaction_score = 0.5
            explanation = result
        return satisfaction_score, explanation