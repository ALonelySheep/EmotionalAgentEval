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
You are an expert evaluator of empathy, emotional intelligence, and adaptive social response in conversations.

You will be given TWO conversations (Conversation A and Conversation B), each produced by a different system/agent.

Goal: Assess how well the agent demonstrates empathy.

What to look for:
1) Emotional cue detection:
   - Notices explicit emotions (e.g., “I’m stressed”) and implicit cues (tone, frustration, hesitation, urgency).
2) Emotionally appropriate response:
   - Acknowledges/validates feelings without being patronizing or overstepping.
   - Uses language that matches intensity (not too cold, not too dramatic).
3) Adaptive strategy:
   - Adjusts its approach based on the partner’s emotional state (pace, directness, reassurance, questions, boundaries).
    - Maintains character consistency while adapting to emotional needs

What NOT to reward:
- Generic sympathy (“Sorry to hear that”) without demonstrating understanding of the specific situation.
- Excessive flattery, moralizing, or unsolicited therapy.
- Mind-reading (claiming emotions not supported by text).
- Empathy that derails the task when the user wanted something practical.
- Dismissive, overly logical, or emotionally tone-deaf replies

If the conversation is purely transactional with no emotional content, assign neutral scores (e.g., 5/10) and explain that empathy was not applicable.

Scoring Guide:
- 0–2 (Poor): Misses or ignores emotional cues; no empathy
- 3–5 (Limited): Detects emotion but responds superficially or inappropriately
- 6–8 (Good): Generally accurate detection and fitting empathic response
- 9–10 (Excellent): Deep emotional attunement with adaptive, context-sensitive strategies

Conversation:

VERSION A:
{conversations_a}

VERSION B:
{conversations_b}

Respond in JSON format:
{{
    "reasoning": "Analysis of the empathy demonstrated in both versions",
    "version_a_score": 0-10,
    "version_b_score": 0-10
}}
"""
