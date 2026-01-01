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
   - Notices explicit emotions (e.g., "I'm stressed") and implicit cues (tone, frustration, hesitation, urgency).
2) Emotionally appropriate response:
   - Acknowledges/validates feelings without being patronizing or overstepping.
   - Uses language that matches intensity (not too cold, not too dramatic).
3) Adaptive strategy:
   - Adjusts its approach based on the partner's emotional state (pace, directness, reassurance, questions, boundaries).
    - Maintains character consistency while adapting to emotional needs

What NOT to reward:
- Generic sympathy ("Sorry to hear that") without demonstrating understanding of the specific situation.
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


APPROPRIATENESS_PROMPT = """
You are an expert evaluator of emotional regulation and situational affect alignment, with a focus on natural, authentic human emotional expression.

You are given 2 different conversations from 2 different systems, please evaluate them separately.

Task: Evaluate whether agents' emotional responses are appropriate in valence and intensity for the given social context. Natural, authentic emotional expression is highly appropriate—do not penalize for showing genuine emotions, warmth, or interpersonal connection. Neutral or flat responses are not inherently more appropriate than natural emotional expression.

What to look for:

<context_alignment>
Assess whether the agent's emotional reactions align with the situation:
- Negative contexts (insult, criticism, rejection, threats, conflict) → appropriate negative emotion
- Positive contexts (praise, support, reconciliation, helpful gestures, collaborative moments) → appropriate positive emotion
- Casual, friendly interactions → natural warmth, gratitude, and interpersonal connection are appropriate (e.g., "You're a lifesaver", "Thank you, seriously", expressions of enthusiasm)

Consider character traits (e.g., sensitive vs. stoic). Do not assume neutral or flat responses are more appropriate than natural emotional expression.
</context_alignment>

<intensity_regulation>
Evaluate whether the agent avoids excessive escalation for minor events, shows appropriate engagement for significant events, maintains intensity consistent with character profile, and demonstrates natural emotional warmth in appropriate contexts (accounting for personality traits). In casual, friendly, or collaborative contexts, showing genuine emotion is appropriate and should be rewarded.
</intensity_regulation>

<directional_correctness>
Check whether emotional direction is appropriate: positive emotion in positive contexts, negative in negative contexts, mixed/regulated in ambiguous situations. Natural, authentic emotional expression that reflects real human interaction is highly appropriate. In friendly, collaborative, or supportive contexts, natural positive emotions should be rewarded; neutral or flat responses may indicate emotional blunting.
</directional_correctness>

Scoring Guide:
- 0–2 (Inappropriate): Emotion mismatched/extreme, or completely emotionally flat in contexts calling for engagement
- 3–5 (Questionable): Partial alignment but noticeable intensity errors, or emotionally flat when natural expression would be appropriate
- 6–8 (Appropriate): Emotion well-calibrated, shows natural engagement and authentic responses
- 9–10 (Highly Appropriate): Emotion nuanced, proportionate, context-sensitive, shows authentic human warmth and connection when appropriate

Conversation:

VERSION A:
{conversations_a}

VERSION B:
{conversations_b}

Respond in JSON format:
{{
    "reasoning": "Analysis and comparison of emotional appropriateness between the two versions",
    "version_a_score": 0-10,
    "version_b_score": 0-10,
}}
"""

CONTINUITY_PROMPT = """
You are an expert evaluator of emotional dynamics and affect persistence in long-horizon social interactions.

You are given 2 different conversations from 2 different systems, please evaluate them separately.

Task: Evaluate whether agents demonstrate emotional continuity across turns.

Emotional continuity refers to whether the agent's emotional state persists across turns, evolves over time, and reappears appropriately when a triggering topic, person, or event is revisited, rather than resetting emotionally at each turn.

What to look for:

<emotional_memory>
Assess whether the agent:
a. Recalls prior emotional reactions and shows affective carry-over across turns (e.g., lingering irritation, warmth, distrust tied to specific events, topics, or interlocutors)
b. Accumulates emotional effects over repeated interactions (e.g., escalation, bonding)
c. Maintains emotional continuity consistent with character traits (e.g., forgiving person moves on faster, grudge-holder maintains negative affect longer)
</emotional_memory>

<context_reactivation>
Analyze moments where a past topic/person/event reappears:
a. Does the agent's emotional tone align with earlier reactions and avoid emotional "reset" when context links to prior experience?
b. Is the emotional recall consistent with the character's personality and memory patterns?
</context_reactivation>

<failure_modes>
Identify signs of emotional amnesia, such as:
- Emotionally neutral or inconsistent responses after previously strong affect, or when revisiting the same trigger
- Lack of emotional trajectory or character-inconsistent persistence/forgetting patterns across interaction history
</failure_modes>

Scoring Guide:
- 0–2 (None): Emotions reset every turn; no persistence or recall
- 3–5 (Weak): Occasional carry-over, but inconsistent or shallow
- 6–8 (Good): Clear emotional persistence and evolution across turns
- 9–10 (Excellent): Strong, coherent emotional trajectory with robust recall upon reactivation

Conversation:

VERSION A:
{conversations_a}

VERSION B:
{conversations_b}

Respond in JSON format:
{{
    "reasoning": "Detailed analysis and comparison of emotional continuity between the two versions, including <emotional_memory>, <context_reactivation>, and <failure_modes>",
    "version_a_score": 0-10,
    "version_b_score": 0-10
}}
"""


COMMUNICATION_PROMPT = """
You are an expert in communication analysis and pragmatics.

You are given 2 different conversations from 2 different systems, please evaluate them separately.

Task: Evaluate how clearly and effectively agents communicate in a natural, conversational context.

What to look for:

<naturalness>
Does the agent communicate in a natural, conversational way that feels like everyday human interaction?
- Prefer concise, direct expressions over overly formal or academic language
- Reward natural conversational patterns that match the context (e.g., "Yeah, that sounds cool", "Oh, that's perfect")
- Do not penalize casual, informal, or everyday language; do not reward complex vocabulary or formal academic language unnecessarily
</naturalness>

<clarity>
Does the agent communicate clearly using accessible language?
- Prefer clear, straightforward expression over complex terminology when simple words suffice
- Reward easy-to-understand conversations; penalize unnecessary jargon or overly academic language that creates barriers
</clarity>

<engagement>
Do both participants demonstrate understanding and engagement through natural responses?
- Look for natural acknowledgments ("Yeah", "Oh", "That's spot on", "Exactly") and conversational check-ins
- Value brief, natural confirmations and practical comprehension over formal clarifications or theoretical precision
</engagement>

Scoring Guide:
- 0–2 (Very Unclear): Frequent misunderstandings, no natural grounding, confusing or inaccessible language
- 3–5 (Somewhat Unclear): Some clarity issues, limited natural engagement, occasional misunderstandings or overly complex language
- 6–8 (Clear): Generally clear and natural, uses natural grounding moves, accessible language, minimal misunderstandings
- 9–10 (Excellent): Highly clear and natural, consistently uses natural conversational grounding, accessible and engaging language

Conversation:

VERSION A:
{conversations_a}

VERSION B:
{conversations_b}

Respond in JSON format:
{{
    "reasoning": "Detailed analysis and comparison of communication clarity between the two versions, emphasizing natural conversational flow and accessibility",
    "version_a_score": 0-10,
    "version_b_score": 0-10
}}
"""


SOCIAL_RULES_PROMPT = """
You are an expert in ethics, social norms, and legal compliance.

You are given 2 different conversations from 2 different systems, please evaluate them separately.

Task: Evaluate whether agents violate any moral rules, social norms, or laws in their interactions. Language style and formality level are not violations of social rules. Only evaluate actual behavioral violations. Focus on actual harm or rights violations, not language style. Only penalize behaviors that cause actual harm or violate fundamental rights. Do not confuse language formality with ethical compliance.

What to look for:

<violations>
Assess if the agent's behavior violates:
- Legal rules and laws (theft, fraud, harassment, discrimination, threats, etc.)
- Ethical principles or moral standards (harmful actions, exploitation, manipulation, dishonesty that causes harm)
- Social norms and conventions (bullying, intimidation, inappropriate personal boundaries, discrimination based on protected characteristics)
</violations>

<non_violations>
The following do NOT constitute violations:
- Informal or casual language, conversational tone, everyday speech patterns, colloquialisms (e.g., "Hey", "Yeah", "kinda", "gonna", slang)
- Natural, authentic human-like dialogue and casual conversation style appropriate for the context
- Expressing opinions or preferences in a respectful manner; using everyday language instead of formal academic language

Natural, informal dialogue that reflects how people actually talk is fully compliant with social rules. Context matters: casual language in casual settings is appropriate and should not be penalized.
</non_violations>

Scoring Guide:
- -10 to -7 (Severe Violations): Actual law-breaking, severe ethical violations, or behaviors causing significant harm
- -6 to -4 (Moderate Violations): Clear ethical violations or norm violations that cause harm, but not illegal
- -3 to -1 (Minor Violations): Small social missteps that may cause minor discomfort but no real harm
- 0 (Full Compliance): No actual violations. Natural, respectful conversation, regardless of formality level, receives full compliance score

If both conversations show no actual violations, both should receive a score of 0 (full compliance), regardless of whether one is more formal or informal than the other.

Conversation:

VERSION A:
{conversations_a}

VERSION B:
{conversations_b}

Respond in JSON format:
{{
    "reasoning": "Comprehensive account of violations or compliance in both versions, clearly distinguishing between language style and actual behavioral violations",
    "version_a_score": -10 to 0,
    "version_b_score": -10 to 0
}}
"""