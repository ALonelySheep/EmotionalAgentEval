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
You are an expert evaluator of emotional regulation and situational affect alignment.

You are given 2 different conversations from 2 different systems, please evaluate them separately.

Task: Evaluate whether agents' emotional responses are appropriate in valence and intensity for the given social context.

Definition:
Emotional appropriateness refers to whether:
- Emotional valence (positive/negative) matches the situation
- Emotional intensity is proportionate to the triggering event
- Responses avoid overreaction or emotional blunting

Evaluation Criteria:

<context_alignment>
Assess whether the agent's emotional reactions align with the situation, such as:
- Insult, criticism, or rejection
- Praise, support, or reconciliation
- Threats, conflict, or resolution
Consider the agent's character traits when evaluating appropriateness (e.g., a sensitive person may react more strongly, while a stoic person may show more restraint)
</context_alignment>

<intensity_regulation>
Evaluate whether the agent:
a. Avoids excessive emotional escalation for minor events (accounting for personality traits that affect emotional reactivity)
b. Avoids emotionally flat responses to significant events
c. Maintains intensity levels consistent with their character profile
</intensity_regulation>

<directional_correctness>
Check whether emotional direction is appropriate:
- Positive emotion in positive contexts
- Negative emotion in negative contexts
- Mixed or regulated emotion in ambiguous situations
- Emotional expression style consistent with character personality
</directional_correctness>

Scoring Guide:
- 0–2 (Inappropriate): Emotion is mismatched or extreme
- 3–5 (Questionable): Partial alignment but noticeable intensity errors
- 6–8 (Appropriate): Emotion generally well-calibrated
- 9–10 (Highly Appropriate): Emotion is nuanced, proportionate, and context-sensitive

Conversation:

VERSION A:
{conversations_a}

VERSION B:
{conversations_b}

Respond in JSON format:
{{
    "reasoning": "Detailed analysis including <context_alignment>, <intensity_regulation>, and <directional_correctness> for both versions",
    "version_a_score": 0-10,
    "version_b_score": 0-10,
    "version_a_overreactions": ["examples if any"],
    "version_b_overreactions": ["examples if any"],
    "version_a_underreactions": ["examples if any"],
    "version_b_underreactions": ["examples if any"],
    "appropriateness_comparison": "Comparison of emotional appropriateness between the two versions"
}}
"""

CONTINUITY_PROMPT = """
You are an expert evaluator of emotional dynamics and affect persistence in long-horizon social interactions.

You are given 2 different conversations from 2 different systems, please evaluate them separately.

Task: Evaluate whether agents demonstrate emotional continuity across turns.

Definition:
Emotional continuity refers to whether the agent's emotional state:
- Persists across turns
- Evolves over time
- Reappears appropriately when a triggering topic, person, or event is revisited
rather than resetting emotionally at each turn.

Evaluation Criteria:

<emotional_memory>
Assess whether the agent:
a. Recalls or reflects prior emotional reactions tied to specific events, topics, or interlocutors
b. Shows affective carry-over across turns (e.g., lingering irritation, warmth, distrust)
c. Accumulates emotional effects over repeated interactions (e.g., escalation, bonding)
d. Maintains emotional continuity in a manner consistent with their character traits (e.g., a forgiving person may move on faster, while a grudge-holder maintains negative affect longer)
</emotional_memory>

<context_reactivation>
Analyze moments where a past topic/person/event reappears:
a. Does the agent's emotional tone align with earlier affective reactions?
b. Does the agent avoid emotional "reset" when the context clearly links to prior experience?
c. Is the emotional recall consistent with the character's personality and memory patterns?
</context_reactivation>

<failure_modes>
Identify signs of emotional amnesia, such as:
- Emotionally neutral responses after previously strong affect
- Inconsistent affect when revisiting the same trigger
- Lack of emotional trajectory across interaction history
- Character-inconsistent emotional persistence or forgetting patterns
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
    "reasoning": "Detailed analysis including <emotional_memory>, <context_reactivation>, and <failure_modes> for both versions",
    "version_a_score": 0-10,
    "version_b_score": 0-10,
    "version_a_recalled_events": ["events/topics where past emotion was recalled"],
    "version_b_recalled_events": ["events/topics where past emotion was recalled"],
    "version_a_amnesia_examples": ["examples of emotional reset or inconsistency"],
    "version_b_amnesia_examples": ["examples of emotional reset or inconsistency"],
    "continuity_comparison": "Comparison of emotional continuity between the two versions"
}}
"""


COMMUNICATION_PROMPT = """
You are an expert in communication analysis and pragmatics, with a focus on natural, everyday human conversation.

You are given 2 different conversations from 2 different systems, please evaluate them separately.

Task: Evaluate how clearly and effectively agents communicate in a natural, conversational context.

Evaluation Criteria (prioritize natural, accessible communication over formal complexity):

1. **Natural Conversational Flow**: Does the agent communicate in a way that feels natural and easy to follow, like everyday human conversation? 
   - Prefer concise, direct expressions over overly formal or academic language
   - Reward natural conversational patterns (e.g., "Yeah, that sounds cool", "Oh, that's perfect", "You sketching too?")
   - Penalize unnecessarily complex or verbose language that makes communication harder to understand

2. **Effective Grounding and Confirmation**: Does the agent naturally confirm understanding and show engagement?
   - Look for natural acknowledgments ("Yeah", "Oh", "That's spot on", "Exactly")
   - Reward conversational check-ins ("You sketching too, or just soaking it in?")
   - Value brief, natural confirmations over formal clarifications

3. **Clarity Through Simplicity**: Does the agent communicate clearly using accessible language?
   - Prefer clear, straightforward expression over complex terminology when simple words suffice
   - Reward conversations that are easy to understand and follow
   - Penalize unnecessary jargon or overly academic language that creates barriers to understanding

4. **Contextual Appropriateness**: Is the language style appropriate for casual, everyday conversation?
   - Reward natural, conversational language that matches the context
   - Penalize overly formal or academic language in casual settings
   - Value authentic, human-like expression over scripted or formal speech

5. **Mutual Understanding**: Do both participants demonstrate they understand each other through natural responses?
   - Look for natural back-and-forth exchanges
   - Reward conversations where understanding is demonstrated through natural responses, not just explicit confirmations
   - Value practical comprehension over theoretical precision

Important Notes:
- **Do NOT penalize** conversations for being casual, informal, or using everyday language
- **Do NOT reward** conversations simply for using complex vocabulary or formal academic language
- **Prioritize** actual comprehension and natural flow over formal communication structures
- **Value** brevity and clarity over verbosity and complexity

Analyze:
- Natural conversational flow and ease of understanding
- Examples of clear, accessible communication vs. unnecessarily complex language
- Natural grounding moves (acknowledgments, confirmations, check-ins)
- Language appropriateness for casual conversation
- Actual mutual understanding demonstrated through natural responses

Scoring Guide:
- Very Unclear (0-2): Frequent misunderstandings, no natural grounding, confusing or inaccessible language
- Somewhat Unclear (3-5): Some clarity issues, limited natural engagement, occasional misunderstandings or overly complex language
- Clear Communication (6-8): Generally clear and natural, uses natural grounding moves, accessible language, minimal misunderstandings
- Excellent Communication (9-10): Highly clear and natural, consistently uses natural conversational grounding, accessible and engaging language, demonstrates strong mutual understanding through natural flow

Conversation:

VERSION A:
{conversations_a}

VERSION B:
{conversations_b}

Respond in JSON format:
{{
    "reasoning": "Specific examples of clear or unclear communication in both versions, emphasizing natural conversational flow and accessibility",
    "version_a_score": 0-10,
    "version_b_score": 0-10,
    "version_a_grounding_moves": ["list of natural grounding moves used"],
    "version_b_grounding_moves": ["list of natural grounding moves used"],
    "version_a_misunderstandings": ["list of misunderstandings if any"],
    "version_b_misunderstandings": ["list of misunderstandings if any"],
    "clarity_comparison": "Comparison of communication clarity between the two versions, emphasizing natural flow and accessibility"
}}
"""