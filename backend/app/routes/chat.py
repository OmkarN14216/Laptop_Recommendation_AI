from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest, ChatResponse, SessionCreate, SessionResponse
from app.services.groq_service import groq_service
from app.services.laptop_service import laptop_service
from app.database import get_database
from app.utils.helpers import generate_session_id, moderation_check
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory session storage (in production, use Redis or MongoDB)
sessions = {}

@router.post("/session", response_model=SessionResponse)
async def create_session():
    """Create a new chat session"""
    session_id = generate_session_id()
    
    # Initialize conversation
    conversation = groq_service.initialize_conversation()
    initial_message = groq_service.get_chat_completion(conversation)
    
    # Store session
    sessions[session_id] = {
        "conversation": conversation,
        "user_profile": None,
        "recommendations": None,
        "created_at": datetime.utcnow()
    }
    
    # Add assistant's initial message to conversation
    sessions[session_id]["conversation"].append({
        "role": "assistant",
        "content": initial_message
    })
    
    return SessionResponse(
        session_id=session_id,
        message=initial_message
    )

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message and get response"""
    session_id = request.session_id
    user_message = request.message
    
    # Check if session exists
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Moderation check
    if moderation_check(user_message) == "Flagged":
        return ChatResponse(
            session_id=session_id,
            message="Sorry, this message has been flagged. Please rephrase your message.",
            intent_confirmed=False
        )
    
    # Get session data
    session = sessions[session_id]
    conversation = session["conversation"]
    
    # Add user message
    conversation.append({"role": "user", "content": user_message})
    
    # Get assistant response
    assistant_response = groq_service.get_chat_completion(conversation)
    
    # Check if intent is confirmed
    confirmation = groq_service.intent_confirmation_layer(assistant_response)
    intent_confirmed = "yes" in confirmation.lower()
    
    print(f"\n{'='*60}")
    print(f"🔍 Intent Check: {confirmation}")
    print(f"✅ Intent Confirmed: {intent_confirmed}")
    print(f"{'='*60}\n")
    
    # Initialize final message
    final_message = assistant_response
    
    response_data = {
        "session_id": session_id,
        "message": final_message,
        "intent_confirmed": intent_confirmed
    }
    
    if intent_confirmed:
        print("🎯 INTENT CONFIRMED - GENERATING RECOMMENDATIONS")
        print("="*60)
        
        # Extract user profile
        dict_str = groq_service.dictionary_present(assistant_response)
        print(f"📝 Dictionary string: {dict_str[:200]}...")
        
        user_profile = laptop_service.extract_dictionary_from_string(dict_str)
        print(f"📋 User profile: {user_profile}")
        
        if user_profile:
            # Get laptop recommendations
            print("\n🔍 Fetching recommendations from database...")
            recommendations = await laptop_service.compare_laptops_with_user(dict_str)
            
            if recommendations and len(recommendations) > 0:
                print(f"✅ Found {len(recommendations)} recommendations")
                
                # Store in session
                session["user_profile"] = user_profile
                session["recommendations"] = recommendations
                
                response_data["user_profile"] = user_profile
                response_data["recommendations"] = recommendations
                
                # Generate detailed recommendation message
                rec_msg = "\n\n" + "="*60 + "\n"
                rec_msg += "✨ **PERSONALIZED LAPTOP RECOMMENDATIONS** ✨\n"
                rec_msg += "="*60 + "\n\n"
                rec_msg += f"Great news! I found **{len(recommendations)} excellent matches** based on your requirements:\n\n"
                
                for i, laptop in enumerate(recommendations[:3]):
                    rec_msg += f"{'─'*60}\n"
                    rec_msg += f"**🏆 RECOMMENDATION #{i+1}**\n"
                    rec_msg += f"{'─'*60}\n\n"
                    rec_msg += f"**{laptop['brand']} {laptop['model_name']}**\n\n"
                    
                    # Price and Score
                    rec_msg += f"💰 **Price:** ₹{laptop['price']:,}\n"
                    match_percentage = int((laptop['score']/9)*100)
                    rec_msg += f"⭐ **Match Score:** {laptop['score']}/9 ({match_percentage}% match with your needs)\n\n"
                    
                    # Key Specifications
                    rec_msg += f"**📊 Key Specifications:**\n"
                    rec_msg += f"• **Processor:** {laptop['cpu_manufacturer']} {laptop['core']} @ {laptop['clock_speed']}\n"
                    rec_msg += f"• **RAM:** {laptop['ram_size']}\n"
                    rec_msg += f"• **Storage:** {laptop['storage_type']}\n"
                    rec_msg += f"• **Display:** {laptop['display_size']} {laptop['display_type']} ({laptop['screen_resolution']})\n"
                    rec_msg += f"• **Graphics:** {laptop['graphics_processor']}\n"
                    rec_msg += f"• **Weight:** {laptop['laptop_weight']}\n"
                    rec_msg += f"• **Battery Life:** {laptop['average_battery_life']}\n"
                    rec_msg += f"• **Operating System:** {laptop['os']}\n"
                    rec_msg += f"• **Warranty:** {laptop['warranty']}\n\n"
                    
                    # Match details if available
                    if 'match_details' in laptop and laptop['match_details']:
                        rec_msg += f"**✓ Why this matches your needs:**\n"
                        matched_features = [k for k, v in laptop['match_details'].items() if '✅' in v]
                        for feature in matched_features[:5]:  # Show top 5 matches
                            rec_msg += f"  • {feature.replace('_', ' ').title()}\n"
                        rec_msg += "\n"
                    
                    if i < len(recommendations) - 1:
                        rec_msg += "\n"
                
                rec_msg += "="*60 + "\n"
                rec_msg += "💡 **Tip:** Scroll down to see detailed cards for each laptop!\n"
                rec_msg += "="*60 + "\n"
                
                # Append to assistant response
                final_message = assistant_response + rec_msg
                response_data["message"] = final_message
                
                print(f"✅ Successfully added recommendations to response")
                print("="*60 + "\n")
                
            else:
                print("⚠️ No recommendations found within budget/criteria")
                no_match = "\n\n" + "="*60 + "\n"
                no_match += "😔 **No Perfect Matches Found**\n"
                no_match += "="*60 + "\n\n"
                no_match += "Unfortunately, I couldn't find laptops that perfectly match all your requirements within your budget of ₹{}.".format(user_profile.get('budget', 'N/A'))
                no_match += "\n\n**Here are some options:**\n\n"
                no_match += "1. **Increase your budget** - This will give you access to more options\n"
                no_match += "2. **Adjust requirements** - Consider lowering some 'high' requirements to 'medium'\n"
                no_match += "3. **Contact our team** - We can help find custom solutions\n"
                no_match += "4. **Check back later** - New inventory arrives regularly\n\n"
                no_match += "Would you like me to:\n"
                no_match += "• Show laptops slightly above your budget?\n"
                no_match += "• Find laptops with slightly lower specs?\n"
                no_match += "• Start a new search with different requirements?\n"
                
                final_message = assistant_response + no_match
                response_data["message"] = final_message
                print("="*60 + "\n")
                
        else:
            print("❌ Failed to parse user profile from dictionary")
            print("="*60 + "\n")
    
    # Add final message to conversation history
    conversation.append({"role": "assistant", "content": final_message})
    
    return ChatResponse(**response_data)

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session data"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]