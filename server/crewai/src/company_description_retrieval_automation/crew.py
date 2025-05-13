from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import WebsiteSearchTool
from crewai_tools import ScrapeElementFromWebsiteTool

@CrewBase
class CompanyDescriptionRetrievalAutomationCrew():
    """CompanyDescriptionRetrievalAutomation crew"""

    @agent
    def website_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['website_finder'],
            tools=[WebsiteSearchTool()],
        )

    @agent
    def description_scraper(self) -> Agent:
        return Agent(
            config=self.agents_config['description_scraper'],
            tools=[ScrapeElementFromWebsiteTool()],
        )


    @task
    def find_company_website(self) -> Task:
        return Task(
            config=self.tasks_config['find_company_website'],
            tools=[WebsiteSearchTool()],
        )

    @task
    def extract_company_description(self) -> Task:
        return Task(
            config=self.tasks_config['extract_company_description'],
            tools=[ScrapeElementFromWebsiteTool()],
        )


    @crew
    def crew(self) -> Crew:
        """Creates the CompanyDescriptionRetrievalAutomation crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
