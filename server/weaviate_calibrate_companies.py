import os
import weaviate
from weaviate.auth import Auth
from weaviate.classes.config import Configure, Property, DataType
from weaviate.agents.query import QueryAgent
from weaviate.agents.utils import print_query_agent_response
from dotenv import load_dotenv
from company_data import COMPANY_DATA
import argparse

# Load environment variables
load_dotenv()

# Best practice: store your credentials in environment variables
weaviate_url = os.environ["WEAVIATE_URL"]
weaviate_api_key = os.environ["WEAVIATE_API_KEY"]

def setup_weaviate_client():
    """Set up and return a Weaviate client."""
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=Auth.api_key(weaviate_api_key),
    )
    print(f"Client ready: {client.is_ready()}")
    return client

def delete_collections(client):
    """Delete existing collections if they exist."""
    collections = ["CompanyInfo", "Products", "UseCases"]
    for collection_name in collections:
        try:
            client.collections.delete(collection_name)
            print(f"Deleted collection: {collection_name}")
        except:
            print(f"Collection {collection_name} does not exist or could not be deleted")

def create_collections(client):
    """Create the Company collections."""
    # Company Info collection
    client.collections.create(
        "CompanyInfo",
        description="Information about the company, including founding details and general description.",
        vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
        properties=[
            Property(name="name", data_type=DataType.TEXT),
            Property(
                name="description",
                data_type=DataType.TEXT,
                description="Detailed description of the company",
            ),
            Property(
                name="founded_year",
                data_type=DataType.INT,
                description="Year the company was founded",
            ),
            Property(
                name="founders",
                data_type=DataType.TEXT_ARRAY,
                description="List of company founders",
            ),
            Property(
                name="sources",
                data_type=DataType.TEXT_ARRAY,
                description="Sources of information",
            ),
        ],
    )

    # Products collection
    client.collections.create(
        "Products",
        description="Information about company products and services.",
        vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
        properties=[
            Property(name="name", data_type=DataType.TEXT),
            Property(
                name="description",
                data_type=DataType.TEXT,
                description="Detailed description of the product",
            ),
            Property(
                name="type",
                data_type=DataType.TEXT,
                description="Type of product (e.g., Open Source, Cloud Service)",
            ),
            Property(
                name="sources",
                data_type=DataType.TEXT_ARRAY,
                description="Sources of information",
            ),
        ],
    )

    # Use Cases collection
    client.collections.create(
        "UseCases",
        description="Information about company use cases and applications.",
        vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
        properties=[
            Property(name="name", data_type=DataType.TEXT),
            Property(
                name="description",
                data_type=DataType.TEXT,
                description="Detailed description of the use case",
            ),
            Property(
                name="sources",
                data_type=DataType.TEXT_ARRAY,
                description="Sources of information",
            ),
        ],
    )

def check_collections_exist(client):
    """Check if collections already exist and have data."""
    try:
        company_info = client.collections.get("CompanyInfo")
        products = client.collections.get("Products")
        use_cases = client.collections.get("UseCases")
        
        # More stringent check - we expect at least 4 companies
        has_sufficient_data = (
            len(company_info) >= 4 and  # At least 4 companies
            len(products) > 0 and 
            len(use_cases) > 0
        )
        
        if not has_sufficient_data:
            return False
            
        return True
    except Exception as e:
        print(f"Error checking collections: {e}")
        return False

def populate_database(client):
    """Populate the database with company information."""
    # Check if collections already exist and have data
    if check_collections_exist(client):
        print("Collections already exist and contain data. Skipping data import.")
        return

    # Get collections
    company_info_collection = client.collections.get("CompanyInfo")
    products_collection = client.collections.get("Products")
    use_cases_collection = client.collections.get("UseCases")

    # Add company info for all companies
    companies = ["company_info", "comet", "llamaindex", "canva"]
    with company_info_collection.batch.fixed_size(batch_size=len(companies)) as batch:
        # Add main Weaviate company info
        batch.add_object(properties=COMPANY_DATA["company_info"])
        
        # Add other companies' info
        for company in ["comet", "llamaindex", "canva"]:
            if company in COMPANY_DATA and "company_info" in COMPANY_DATA[company]:
                batch.add_object(properties=COMPANY_DATA[company]["company_info"])

    # Add products for all companies
    all_products = []
    all_products.extend(COMPANY_DATA["products"])
    for company in ["comet", "llamaindex", "canva"]:
        if company in COMPANY_DATA and "products" in COMPANY_DATA[company]:
            all_products.extend(COMPANY_DATA[company]["products"])

    with products_collection.batch.fixed_size(batch_size=len(all_products)) as batch:
        for product in all_products:
            batch.add_object(properties=product)

    # Add use cases for all companies
    all_use_cases = []
    all_use_cases.extend(COMPANY_DATA["use_cases"])
    for company in ["comet", "llamaindex", "canva"]:
        if company in COMPANY_DATA and "use_cases" in COMPANY_DATA[company]:
            all_use_cases.extend(COMPANY_DATA[company]["use_cases"])

    with use_cases_collection.batch.fixed_size(batch_size=len(all_use_cases)) as batch:
        for use_case in all_use_cases:
            batch.add_object(properties=use_case)

    # Print collection sizes
    print(f"Size of the CompanyInfo collection: {len(company_info_collection)}")
    print(f"Size of the Products collection: {len(products_collection)}")
    print(f"Size of the UseCases collection: {len(use_cases_collection)}")

def setup_agent(client):
    """Set up the query agent."""
    agent = QueryAgent(
        client=client,
        collections=["CompanyInfo", "Products", "UseCases"],
        system_prompt="You are a helpful assistant that provides information about Weaviate company, its products, and use cases. "
        "Always provide detailed and accurate information based on the available data. "
        "If you don't have information about a topic, clearly state that the information is not available in the database.",
    )
    return agent

def run_example_queries(agent, example_numbers):
    """Run specified example queries."""
    if 1 in example_numbers:
        print("\n=== Example Query 1: Weaviate Products ===")
        response = agent.run("What are Weaviate's main products and their descriptions?")
        print_query_agent_response(response)

    if 2 in example_numbers:
        print("\n=== Example Query 2: Crew AI Information ===")
        response = agent.run("What is Crew AI? Can you tell me about its features and capabilities?")
        print_query_agent_response(response)

def query_weaviate_agent(prompt: str) -> str:
    """Query the Weaviate agent with a single prompt and return the response as a string."""
    client = None
    try:
        client = setup_weaviate_client()
        agent = setup_agent(client)
        response = agent.run(prompt)
        # The response may be a dict or object; get the text/answer part
        if isinstance(response, dict) and 'answer' in response:
            return response['answer']
        return str(response)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if client:
            client.close()

def main():
    """Main function to run the complete example."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run Weaviate company information examples')
    parser.add_argument('--examples', type=int, nargs='+', default=[1, 2],
                      help='Example numbers to run (1: Weaviate Products, 2: Crew AI Information)')
    parser.add_argument('--reinit', action='store_true',
                      help='Delete existing collections and reinitialize them')
    args = parser.parse_args()

    try:
        # Set up client
        client = setup_weaviate_client()

        # Delete and recreate collections if --reinit flag is set
        if args.reinit:
            print("Reinitializing collections...")
            delete_collections(client)
            create_collections(client)
            populate_database(client)

        # Set up agent
        agent = setup_agent(client)

        # Run specified example queries
        run_example_queries(agent, args.examples)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Clean up
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main()

"""
Available Commands:

1. Run all examples (default):
   python weaviate_calibrate_companies.py

2. Run specific examples:
   python weaviate_calibrate_companies.py --examples 1
   python weaviate_calibrate_companies.py --examples 2
   python weaviate_calibrate_companies.py --examples 1 2

3. Reinitialize collections (wipe and recreate):
   python weaviate_calibrate_companies.py --reinit

4. Combine reinitialization with specific examples:
   python weaviate_calibrate_companies.py --reinit --examples 1
   python weaviate_calibrate_companies.py --reinit --examples 2
   python weaviate_calibrate_companies.py --reinit --examples 1 2

Example Queries:
1. Weaviate Products: "What are Weaviate's main products and their descriptions?"
2. Crew AI Information: "What is Crew AI? Can you tell me about its features and capabilities?"

Note: Make sure your .env file contains the required environment variables:
WEAVIATE_URL=your_weaviate_url
WEAVIATE_API_KEY=your_weaviate_api_key
""" 