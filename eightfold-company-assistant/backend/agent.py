from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import json
from typing import Dict, Tuple
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SESSION_STORE: Dict[str, SessionState] = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str
    persona: Optional[str] = "efficient"

class ChatResponse(BaseModel):
    reply: str
    mode: str
    company: Optional[str] = None
    account_plan: Optional[Dict[str, str]] = None

class SessionState(BaseModel):
    mode: str = "discovery"
    target_company: Optional[str] = None
    persona: str = "efficient"
    research_notes: List[str] = []
    account_plan: Dict[str, str] = {}

def get_session_state(session_id: str) -> SessionState:
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = SessionState()
    return SESSION_STORE[session_id]

def call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    if json_mode:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )
    else:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    return response.choices[0].message.content

def extract_company_name(user_message: str) -> str:
    system = (
        "You extract company names from text. "
        "Return ONLY the company name as plain text, or an empty string if not sure."
    )
    name = call_llm(system, user_message, json_mode=False).strip()
    if len(name.split()) > 6:
        return ""
    return name

def run_research_for_company(company: str, persona: str) -> Tuple[str, str]:
    system = f"""
You are an AI company research assistant building account plans.

You ALWAYS:
1) Break research into steps (company overview, products, market, recent news, hiring, risks).
2) Mention research updates explicitly like:
   - "Step 1: Looking at company overview..."
   - "Step 2: Checking recent news..."
3) If you see conflicting info, say so and ask if the user wants a deeper dive.
4) At the end, give a concise bullet summary that will feed into an account plan.

User persona: {persona}.
- efficient => be concise.
- confused => be more guiding and explanatory.
- chatty => friendly tone, but still structured.
- edge => robust to weird questions, and gently pull back to company research.

Do NOT generate the full account plan here, only research updates + a summary.
"""
    user = f"Research the company '{company}' for an enterprise account plan. Show your steps and conflicts if any."
    reply = call_llm(system, user, json_mode=False)
    research_summary = reply
    return reply, research_summary

def generate_account_plan(company: str, research_notes: str, persona: str) -> Dict[str, str]:
    system = f"""
You are creating a structured enterprise account plan based on research.

Return STRICT JSON with keys:
- company_overview
- key_initiatives
- org_map_and_stakeholders
- current_tech_landscape
- opportunities_for_us
- risks_and_red_flags
- next_steps

User persona: {persona}.
Write crisp, practical content, no fluff. Prefer 3–6 bullet points per section.
"""
    user = f"""
Company: {company}

Research notes:
{research_notes}

Create the account plan JSON now.
"""
    json_text = call_llm(system, user, json_mode=True)
    plan = json.loads(json_text)
    return plan

def edit_account_plan(
    company: str,
    plan: Dict[str, str],
    user_message: str,
    persona: str,
) -> Tuple[Dict[str, str], str]:
    system = f"""
You help users edit an account plan.

You MUST return JSON with:
- section_key: one of
  ["company_overview", "key_initiatives", "org_map_and_stakeholders",
   "current_tech_landscape", "opportunities_for_us",
   "risks_and_red_flags", "next_steps"]
- updated_text: full updated content for that section (overwrite previous).

Be helpful and follow the user's instructions.
Persona: {persona}.
"""
    user = f"""
Company: {company}

Current plan (JSON):
{json.dumps(plan)}

User edit request:
{user_message}
"""
    raw = call_llm(system, user, json_mode=True)
    data = json.loads(raw)
    section = data.get("section_key")
    updated_text = data.get("updated_text", "")

    if section and updated_text:
        plan[section] = updated_text

    explanation = f"I've updated **{section}** based on your feedback."
    return plan, explanation

def handle_user_message(session_id: str, message: str, persona: str):
    state = get_session_state(session_id)
    state.persona = persona

    if state.mode == "discovery":
        company = extract_company_name(message)
        if not company:
            return {
                "reply": (
                    "Hi! I’m your Company Research Assistant.\n\n"
                    "Tell me which company to research, e.g. **“Research Zeta company”**."
                ),
                "mode": state.mode,
                "company": None,
                "account_plan": None,
            }

        state.target_company = company
        state.mode = "research"
        reply = (
            f"Great, I’ll research **{company}**.\n\n"
            "I’ll start with company overview and recent news, then move to org map, tech landscape, "
            "opportunities, and risks.\n\n"
            "You can also tell me if you want a specific focus (e.g. “focus on AI initiatives”)."
        )
        return {
            "reply": reply,
            "mode": state.mode,
            "company": company,
            "account_plan": None,
        }

    if state.mode == "research":
        if not state.target_company:
            state.mode = "discovery"
            return {
                "reply": "I lost track of the company name 😅. Could you tell me the company again?",
                "mode": state.mode,
                "company": None,
                "account_plan": None,
            }

        research_reply, research_summary = run_research_for_company(
            state.target_company, state.persona
        )
        state.research_notes.append(research_summary)

        state.mode = "planning"
        reply = (
            f"{research_reply}\n\n"
            "Based on this, I can now generate a structured account plan.\n"
            "Type **“generate plan”** or tell me what to focus on "
            "(e.g. “focus on EMEA enterprise deals”)."
        )
        return {
            "reply": reply,
            "mode": state.mode,
            "company": state.target_company,
            "account_plan": None,
        }

    if state.mode == "planning":
        if "generate plan" in message.lower() or "account plan" in message.lower():
            all_notes = "\n\n".join(state.research_notes)
            plan = generate_account_plan(
                state.target_company,
                all_notes,
                state.persona,
            )
            state.account_plan = plan
            state.mode = "editing"

            pretty = []
            for key, text in plan.items():
                pretty.append(f"### {key.replace('_', ' ').title()}\n{text}")
            plan_text = "\n\n".join(pretty)

            reply = (
                f"Here’s the initial account plan for **{state.target_company}**:\n\n"
                f"{plan_text}\n\n"
                "You can say things like:\n"
                "- “Edit opportunities_for_us to focus on AI products”\n"
                "- “Rewrite risks_and_red_flags to be shorter”\n"
                "- “Update next_steps for an enterprise sales motion”"
            )
            return {
                "reply": reply,
                "mode": state.mode,
                "company": state.target_company,
                "account_plan": state.account_plan,
            }
        else:
            all_notes = "\n\n".join(state.research_notes) + "\n\nUser focus: " + message
            plan = generate_account_plan(
                state.target_company,
                all_notes,
                state.persona,
            )
            state.account_plan = plan
            state.mode = "editing"

            pretty = []
            for key, text in plan.items():
                pretty.append(f"### {key.replace('_', ' ').title()}\n{text}")
            plan_text = "\n\n".join(pretty)

            reply = (
                "Got it, I’ve tailored the plan based on your preferences.\n\n"
                f"{plan_text}\n\n"
                "You can now ask me to tweak specific sections."
            )
            return {
                "reply": reply,
                "mode": state.mode,
                "company": state.target_company,
                "account_plan": state.account_plan,
            }

    if state.mode == "editing":
        if not state.account_plan:
            state.mode = "planning"
            return {
                "reply": "Looks like we don’t have an account plan yet. Say **“generate plan”** to create one.",
                "mode": state.mode,
                "company": state.target_company,
                "account_plan": None,
            }

        updated_plan, explanation = edit_account_plan(
            state.target_company,
            state.account_plan,
            message,
            state.persona,
        )
        state.account_plan = updated_plan

        pretty = []
        for key, text in updated_plan.items():
            pretty.append(f"### {key.replace('_', ' ').title()}\n{text}")
        plan_text = "\n\n".join(pretty)

        reply = (
            f"{explanation}\n\n"
            "Here is the updated account plan:\n\n"
            f"{plan_text}\n\n"
            "You can continue refining any section or ask for a quick summary."
        )
        return {
            "reply": reply,
            "mode": state.mode,
            "company": state.target_company,
            "account_plan": state.account_plan,
        }

    return {
        "reply": "I’m not sure what to do next. Try telling me a company name or say “generate plan”.",
        "mode": state.mode,
        "company": state.target_company,
        "account_plan": state.account_plan,
    }