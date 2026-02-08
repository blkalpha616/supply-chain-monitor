import os
import smtplib
from email.mime.text import MIMEText
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from crewai_tools import SerperDevTool, FileReadTool

# 1. POWERHOUSE CONFIGURATION (The "Brain")
# We use GPT-4o for commercial-grade reasoning that customers will pay for.
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
search_tool = SerperDevTool()

# 2. AUTOMATED EMAIL SYSTEM (The "Delivery Man")
def send_commercial_report(content):
    sender_email = "blkalpha616@gmail.com"
    receiver_email = "blkalpha616@gmail.com"
    # Pulls the secret 16-digit key from your Render Environment
    password = os.getenv('EMAIL_PASSWORD') 

    msg = MIMEText(content, 'markdown')
    msg['Subject'] = '🚀 NEW DIGITAL PRODUCT READY FOR SALE'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.starttls() # This "unlocks" the connection
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("✅ Success: Product delivered to your inbox.")
    except Exception as e:
        print(f"❌ Delivery Failed: {e}")

# 3. THE CREW: YOUR DIGITAL EMPLOYEES
market_analyst = Agent(
    role='Lead Market Researcher',
    goal='Identify high-demand, low-competition digital niches.',
    backstory="Expert at spotting trends before they go viral. You find the 'Gold Mines'.",
    tools=[search_tool],
    llm=llm,
    verbose=True
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
