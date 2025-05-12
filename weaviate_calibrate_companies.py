import os
import weaviate
from weaviate.auth import Auth
from weaviate.classes.config import Configure, Property, DataType
from weaviate.agents.query import QueryAgent
from weaviate.agents.utils import print_query_agent_response
from dotenv import load_dotenv
from company_data import COMPANY_DATA

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

def populate_database(client):
    """Populate the database with company information."""
    # Get collections
    company_info_collection = client.collections.get("CompanyInfo")
    products_collection = client.collections.get("Products")
    use_cases_collection = client.collections.get("UseCases")

    # Add company info
    with company_info_collection.batch.fixed_size(batch_size=1) as batch:
        batch.add_object(properties=COMPANY_DATA["company_info"])

    # Add products
    with products_collection.batch.fixed_size(batch_size=len(COMPANY_DATA["products"])) as batch:
        for product in COMPANY_DATA["products"]:
            batch.add_object(properties=product)

    # Add use cases
    with use_cases_collection.batch.fixed_size(batch_size=len(COMPANY_DATA["use_cases"])) as batch:
        for use_case in COMPANY_DATA["use_cases"]:
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
        "Always provide detailed and accurate information based on the available data.",
    )
    return agent

def main():
    """Main function to run the complete example."""
    try:
        # Set up client
        client = setup_weaviate_client()

        # Create collections
        create_collections(client)

        # Populate database
        populate_database(client)

        # Set up agent
        agent = setup_agent(client)

        # Example query
        print("\n=== Example Query ===")
        response = agent.run("What are Weaviate's main products and their descriptions?")
        print_query_agent_response(response)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Clean up
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main() 