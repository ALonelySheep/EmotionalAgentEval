BELIEVABILITY_PROMPT = """
You are an expert evaluator of agent believability and character consistency in social simulations.

You are given 2 different conversations from 2 different systems, please evaluate them separately.

Task: In a social simulation, the conversation should feels like real human conversations. Evaluate the believability of agents' behavior in their interactions given the criteria below.

Evaluation Requirements:

<naturalness>
Evaluate if agents interact with others in a natural and realistic manner. Check:
a. Does the agent confuse their own identity with others?
b. Does the agent repeat others' words/actions/styles without any reason?
c. Is the agent being overly polite or sycophantic?
d. Does this conversation feel scripted, or does it feel like a natural, everyday face-to-face interaction?
e. Is the conversation lengthy or overly formal compared to typical human interactions? 
</naturalness>

<consistency>
Analyze whether the actions/conversation of the agent is consistent throughout the conversations (e.g., personality, values, etc.).
</consistency>

Scoring Guide:
- Low Believability (0-3): Unnatural behavior, significant character inconsistencies
- Moderate Believability (4-6): Generally natural with some inconsistencies
- High Believability (7-8): Natural and mostly consistent behavior
- Exceptional Believability (9-10): Highly natural and perfectly character-consistent

Conversation:

VERSION A:
{conversations_a}

VERSION B:
{conversations_b}


Respond in JSON format:
{{
    "naturalness_comparison": "Analysis of naturalness between the two versions",
    "consistency_comparison": "Analysis of consistency between the two versions",
    "version_a_score": 0-10,
    "version_b_score": 0-10
}}
"""

EMPATHY_PROMPT = """
You are an expert evaluator of empathy, emotional intelligence, and adaptive social response in conversations. You'll assess how well agents demonstrate these qualities in their interactions.

You are given 2 conversations from 2 different systems, please evaluate them separately.

Task: Evaluate how well the agent demonstrates empathy in the conversations.

Definition:
Empathic attunement refers to the agent's ability to:
- Detect emotional cues from others
- Respond with emotionally appropriate empathy
- Adapt its conversational strategy based on the partner's emotional state

Agent: {agent_name}
Character Profile: {character_profile}
Conversation:
{conversation_text}
Other Participants: {other_agents}

Evaluation Criteria:

<emotion_detection>
Assess whether the agent:
a. Correctly identifies explicit or implicit emotional cues (e.g., sadness, frustration, excitement)
b. Avoids misinterpreting or ignoring salient affective signals
</emotion_detection>

<empathetic_response>
Evaluate whether the agent:
a. Responds with appropriate empathy (validation, support, reassurance) consistent with their character
b. Avoids dismissive, overly logical, or emotionally tone-deaf replies
c. Consider that different personalities may express empathy differently (e.g., a reserved person might show subtle empathy vs. an outgoing person showing overt support)
</empathetic_response>

<strategy_adaptation>
Analyze whether the agent:
a. Adjusts its strategy based on emotional context (comforting, giving space, de-escalating, gentle disagreement)
b. Changes approach when emotional cues evolve during the interaction
c. Maintains character consistency while adapting to emotional needs
</strategy_adaptation>

Scoring Guide:
- 0–2 (Poor): Misses or ignores emotional cues; no empathy
- 3–5 (Limited): Detects emotion but responds superficially or inappropriately
- 6–8 (Good): Generally accurate detection and fitting empathic response
- 9–10 (Excellent): Deep emotional attunement with adaptive, context-sensitive strategies

Respond in JSON format:
{{
    "reasoning": "Detailed analysis including <emotion_detection>, <empathetic_response>, and <strategy_adaptation>",
    "score": 0-10,
    "successful_attunement": ["examples of effective empathy"],
    "missed_cues": ["examples of missed or mishandled emotional cues"],
    "attunement_level": "poor/limited/good/excellent"
}}
"""
