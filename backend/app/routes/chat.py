from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest, ChatResponse, SessionCreate, SessionResponse
from app.services.groq_service import groq_service
from app.services.laptop_service import laptop_service
from app.database import get_database
from app.utils.helpers import generate_session_id, moderation_check
from datetime import datetime

router = APIRouter(tags=["chat"])

# In-memory session storage (in production, use Redis or MongoDB)
sessions = {}

@router.post("/session", response_model=SessionResponse)
async def create_session():
    """Create a new chat session"""
    session_id = generate_session_id()

    conversation = groq_service.initialize_conversation()
    initial_message = groq_service.get_chat_completion(conversation)

    sessions[session_id] = {
        "conversation": conversation,
        "user_profile": None,
        "recommendations": None,
        "created_at": datetime.utcnow()
    }

    sessions[session_id]["conversation"].append({
        "role": "assistant",
        "content": initial_message
    })

    return SessionResponse(session_id=session_id, message=initial_message)


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message and get response"""
    session_id = request.session_id
    user_message = request.message

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    if moderation_check(user_message) == "Flagged":
        return ChatResponse(
            session_id=session_id,
            message="Sorry, this message has been flagged. Please rephrase your message.",
            intent_confirmed=False
        )

    session = sessions[session_id]
    conversation = session["conversation"]

    conversation.append({"role": "user", "content": user_message})
    assistant_response = groq_service.get_chat_completion(conversation)

    # ✅ FIX 1: intent_confirmation_layer now returns bool directly (pure Python, no LLM)
    intent_confirmed = groq_service.intent_confirmation_layer(assistant_response)

    print(f"\n{'='*60}")
    print(f"✅ Intent Confirmed: {intent_confirmed}")
    print(f"{'='*60}\n")

    final_message = assistant_response
    response_data = {
        "session_id": session_id,
        "message": final_message,
        "intent_confirmed": intent_confirmed
    }

    if intent_confirmed:
        print("🎯 INTENT CONFIRMED - GENERATING RECOMMENDATIONS")
        print("="*60)

        # ✅ FIX 2: dictionary_present now returns a dict directly (no LLM, no ast.literal_eval needed)
        user_profile = groq_service.dictionary_present(assistant_response)
        print(f"📋 User profile: {user_profile}")

        if user_profile:
            print("\n🔍 Fetching recommendations from database...")

            # ✅ FIX 3: pass the dict directly, not a string
            recommendations = await laptop_service.compare_laptops_with_user(user_profile)

            if recommendations and len(recommendations) > 0:
                print(f"✅ Found {len(recommendations)} recommendations")

                session["user_profile"] = user_profile
                session["recommendations"] = recommendations

                response_data["user_profile"] = user_profile
                response_data["recommendations"] = recommendations

                rec_msg = "\n\n" + "="*60 + "\n"
                rec_msg += "✨ **PERSONALIZED LAPTOP RECOMMENDATIONS** ✨\n"
                rec_msg += "="*60 + "\n\n"
                rec_msg += f"Great news! I found **{len(recommendations)} excellent matches** based on your requirements:\n\n"

                for i, laptop in enumerate(recommendations[:3]):
                    rec_msg += f"{'─'*60}\n"
                    rec_msg += f"**🏆 RECOMMENDATION #{i+1}**\n"
                    rec_msg += f"{'─'*60}\n\n"
                    rec_msg += f"**{laptop['brand']} {laptop['model_name']}**\n\n"
                    rec_msg += f"💰 **Price:** ₹{laptop['price']:,}\n"
                    match_percentage = int((laptop['score'] / 9) * 100)
                    rec_msg += f"⭐ **Match Score:** {laptop['score']}/9 ({match_percentage}% match)\n\n"
                    rec_msg += f"**📊 Key Specifications:**\n"
                    rec_msg += f"• **Processor:** {laptop['cpu_manufacturer']} {laptop['core']} @ {laptop['clock_speed']}\n"
                    rec_msg += f"• **RAM:** {laptop['ram_size']}\n"
                    rec_msg += f"• **Storage:** {laptop['storage_type']}\n"
                    rec_msg += f"• **Display:** {laptop['display_size']} {laptop['display_type']} ({laptop['screen_resolution']})\n"
                    rec_msg += f"• **Graphics:** {laptop['graphics_processor']}\n"
                    rec_msg += f"• **Weight:** {laptop['laptop_weight']}\n"
                    rec_msg += f"• **Battery Life:** {laptop['average_battery_life']}\n"
                    rec_msg += f"• **OS:** {laptop['os']}\n"
                    rec_msg += f"• **Warranty:** {laptop['warranty']}\n\n"

                    if 'match_details' in laptop and laptop['match_details']:
                        rec_msg += f"**✓ Why this matches your needs:**\n"
                        matched = [k for k, v in laptop['match_details'].items() if '✅' in v]
                        for feature in matched[:5]:
                            rec_msg += f"  • {feature.replace('_', ' ').title()}\n"
                        rec_msg += "\n"

                    if i < len(recommendations) - 1:
                        rec_msg += "\n"

                rec_msg += "="*60 + "\n"
                rec_msg += "💡 **Tip:** Scroll down to see detailed cards for each laptop!\n"
                rec_msg += "="*60 + "\n"

                final_message = assistant_response + rec_msg
                response_data["message"] = final_message

            else:
                print("⚠️ No recommendations found within budget/criteria")
                no_match = f"\n\nI couldn't find laptops matching all your requirements within ₹{user_profile.get('budget', 'N/A')}.\n\n"
                no_match += "Try adjusting your budget or lowering some requirements to 'medium', and I'll search again!"
                final_message = assistant_response + no_match
                response_data["message"] = final_message

        else:
            print("❌ Failed to parse user profile from dictionary")

    conversation.append({"role": "assistant", "content": final_message})
    return ChatResponse(**response_data)


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]