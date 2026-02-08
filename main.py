import os
import resend
from flask import Flask
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, FileReadTool

# 1. POWERHOUSE CONFIGURATION
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
search_tool = SerperDevTool()

# 2. AUTOMATED EMAIL SYSTEM (The "Delivery Man" via Resend)
resend.api_key = os.getenv('RESEND_API_KEY')

def send_commercial_report(content):
    try:
        params = {
            "from": "onboarding@resend.dev",
            "to": "blkalpha616@gmail.com",
            "subject": "🚀 NEW DIGITAL PRODUCT READY FOR SALE",
            "html": f"<strong>Product Ready:</strong><br><pre>{content}</pre>",
        }
        resend.Emails.send(params)
        print("✅ Success: Email sent via Resend!")
    except Exception as e:
        print(f"❌ Failed: {e}")

# 3. WEB SERVER FOR RENDER (Prevents the "Endless Circle" of Errors)
app = Flask(__name__)

@app.route('/')
def home():
    return "Email Bot is Active and Running"

# --- YOUR AGENTS START BELOW THIS LINE ---


product_architect = Agent(
    role='Digital Product Specialist',
    goal='Design a high-ticket digital asset (PDF, Course, or Tool) based on research.',
    backstory="You turn raw data into something people want to buy for $100+.",
    llm=llm,
    verbose=True
)

# 4. THE AUTONOMOUS TASKS
research_task = Task(
    description="Find 3 trending digital product niches in the AI or Stock Market space for 2026.",
    expected_output="A list of 3 specific gaps in the market with data backing them up.",
    agent=market_analyst
)

creation_task = Task(
    description="Pick the best niche and outline a 'Premium Report' that can be sold on Fiverr. Include a table of contents and a 5-page draft.",
    expected_output="A complete, professional digital product draft ready for a customer.",
    agent=product_architect
)

# 5. EXECUTION LOOP
# 5. EXECUTION LOOP
if __name__ == "__main__":
    print("🤖 AI Crew is starting their 10-hour shift for you...")
    
    my_crew = Crew(
        agents=[market_analyst, product_architect],
        tasks=[research_task, creation_task],
        process=Process.sequential
    )
    
    final_result = my_crew.kickoff()
    
    # Send the email once
    send_commercial_report(str(final_result))
    
    print("🏁 Work complete. Check your email!")

    # --- ADD THIS PART TO KEEP RENDER HAPPY ---
    from flask import Flask
    import os
    
    app = Flask(__name__)
    
    @app.route('/')
    def health_check():
        return "CrewAI Bot is Live!"

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
