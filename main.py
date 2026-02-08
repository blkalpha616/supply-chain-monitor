import os
import resend
from flask import Flask
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, FileReadTool

# 1. POWERHOUSE CONFIGURATION
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
search_tool = SerperDevTool()

# 2. AUTOMATED EMAIL SYSTEM
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

# 3. DEFINE YOUR AGENTS (Must come before Tasks!)
market_analyst = Agent(
    role='Market Research Analyst',
    goal='Find the most profitable niches for digital products in 2026',
    backstory='You are an expert at spotting trends before they go viral.',
    llm=llm,
    verbose=True,
    allow_delegation=False,
    tools=[search_tool]
)

product_architect = Agent(
    role='Digital Product Specialist',
    role_description='Digital Product Specialist',
    goal='Design a high-ticket digital asset (PDF, Course, or Tool) based on research.',
    backstory='You turn raw data into something people want to buy for $100+.',
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

# 5. EXECUTION LOOP & WEB SERVER
if __name__ == "__main__":
    print("🤖 AI Crew is starting their work...")
    
    my_crew = Crew(
        agents=[market_analyst, product_architect],
        tasks=[research_task, creation_task],
        process=Process.sequential
    )
    
    final_result = my_crew.kickoff()
    
    # Send the email once the AI finishes
    send_commercial_report(str(final_result))
    
    print("🏁 Work complete. Check your email!")

    # --- KEEP RENDER HAPPY ---
    app = Flask(__name__)
    
    @app.route('/')
    def health_check():
        return "CrewAI Bot is Active and Running"

    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
