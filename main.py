import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, FileReadTool

# 1. POWERHOUSE CONFIGURATION (The "Brain")
# We use GPT-4o for commercial-grade reasoning that customers will pay for.
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
search_tool = SerperDevTool()

# 2. AUTOMATED EMAIL SYSTEM (The "Delivery Man")
def send_commercial_report(content):
    message = Mail(
        from_email='blkalpha616@gmail.com',
        to_emails='blkalpha616@gmail.com',
        subject='🚀 NEW DIGITAL PRODUCT READY FOR SALE',
        html_content=f'<strong>Product Ready:</strong><br><pre>{content}</pre>'
    )
    try:
        # This uses your new SendGrid Key from Render Environment
        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(f"✅ Web-Door Success: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Web-Door Failed: {e}")

)

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
if __name__ == "__main__":
    print("🤖 AI Crew is starting their 10-hour shift for you...")
    
    my_crew = Crew(
        agents=[market_analyst, product_architect],
        tasks=[research_task, creation_task],
        process=Process.sequential
    )

    final_result = my_crew.kickoff()

    # The Final Hand-off: Send the product to your email automatically
    send_commercial_report(str(final_result))
    
    print("🏁 Work complete. Check your email for your new digital asset.")
