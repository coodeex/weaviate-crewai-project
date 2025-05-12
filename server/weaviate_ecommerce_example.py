import os
import weaviate
from weaviate.auth import Auth
from weaviate.classes.config import Configure, Property, DataType
from datasets import load_dataset
from weaviate.agents.query import QueryAgent
from weaviate.agents.utils import print_query_agent_response
from dotenv import load_dotenv

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
    """Create the Brands and ECommerce collections."""
    # Using `auto-schema` to infer the data schema during import
    client.collections.create(
        "Brands",
        description="A dataset that lists information about clothing brands, their parent companies, average rating and more.",
        vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
    )

    # Explicitly defining the data schema
    client.collections.create(
        "ECommerce",
        description="A dataset that lists clothing items, their brands, prices, and more.",
        vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
        properties=[
            Property(name="collection", data_type=DataType.TEXT),
            Property(
                name="category",
                data_type=DataType.TEXT,
                description="The category to which the clothing item belongs",
            ),
            Property(
                name="tags",
                data_type=DataType.TEXT_ARRAY,
                description="The tags that are assocciated with the clothing item",
            ),
            Property(name="subcategory", data_type=DataType.TEXT),
            Property(name="name", data_type=DataType.TEXT),
            Property(
                name="description",
                data_type=DataType.TEXT,
                description="A detailed description of the clothing item",
            ),
            Property(
                name="brand",
                data_type=DataType.TEXT,
                description="The brand of the clothing item",
            ),
            Property(name="product_id", data_type=DataType.UUID),
            Property(
                name="colors",
                data_type=DataType.TEXT_ARRAY,
                description="The colors on the clothing item",
            ),
            Property(name="reviews", data_type=DataType.TEXT_ARRAY),
            Property(name="image_url", data_type=DataType.TEXT),
            Property(
                name="price",
                data_type=DataType.NUMBER,
                description="The price of the clothing item in USD",
            ),
        ],
    )

def populate_database(client):
    """Populate the database with sample data."""
    brands_dataset = load_dataset(
        "weaviate/agents", "query-agent-brands", split="train", streaming=True
    )
    ecommerce_dataset = load_dataset(
        "weaviate/agents", "query-agent-ecommerce", split="train", streaming=True
    )

    brands_collection = client.collections.get("Brands")
    ecommerce_collection = client.collections.get("ECommerce")

    with brands_collection.batch.fixed_size(batch_size=200) as batch:
        for item in brands_dataset:
            batch.add_object(properties=item["properties"], vector=item["vector"])

    with ecommerce_collection.batch.fixed_size(batch_size=200) as batch:
        for item in ecommerce_dataset:
            batch.add_object(properties=item["properties"], vector=item["vector"])

    failed_objects = brands_collection.batch.failed_objects
    if failed_objects:
        print(f"Number of failed imports: {len(failed_objects)}")
        print(f"First failed object: {failed_objects[0]}")

    print(f"Size of the ECommerce dataset: {len(ecommerce_collection)}")
    print(f"Size of the Brands dataset: {len(brands_collection)}")

def setup_agents(client):
    """Set up the basic and multilingual agents."""
    # Basic agent
    agent = QueryAgent(
        client=client,
        collections=["ECommerce", "Brands"],
    )

    # Multilingual agent
    multi_lingual_agent = QueryAgent(
        client=client,
        collections=["ECommerce", "Brands"],
        system_prompt="You are a helpful assistant that always generates the final response in the user's language. "
        "You may have to translate the user query to perform searches. But you must always respond to the user in their own language.",
    )

    return agent, multi_lingual_agent

def run_example_queries(agent, multi_lingual_agent):
    """Run example queries to demonstrate the agents' capabilities."""
    # Example 1: Basic query
    print("\n=== Example 1: Basic Query ===")
    response = agent.run(
        "I like vintage clothes, can you list me some options that are less than $200?"
    )
    print_query_agent_response(response)

    # Example 2: Follow-up query
    print("\n=== Example 2: Follow-up Query ===")
    new_response = agent.run(
        "What about some nice shoes, same budget as before?", context=response
    )
    print_query_agent_response(new_response)

    # Example 3: Aggregation query
    print("\n=== Example 3: Aggregation Query ===")
    response = agent.run("What is the the name of the brand that lists the most shoes?")
    print_query_agent_response(response)

    # Example 4: Multi-collection query
    print("\n=== Example 4: Multi-collection Query ===")
    response = agent.run(
        "Does the brand 'Loom & Aura' have a parent brand or child brands and what countries do they operate from? "
        "Also, what's the average price of a shoe from 'Loom & Aura'?"
    )
    print_query_agent_response(response)

    # Example 5: Multilingual query
    print("\n=== Example 5: Multilingual Query ===")
    response = multi_lingual_agent.run('"Eko & Stitch"は英国に支店または関連会社がありますか？')
    print(response.final_answer)

def main():
    """Main function to run the complete example."""
    try:
        # Set up client
        client = setup_weaviate_client()

        # Create collections
        create_collections(client)

        # Populate database
        populate_database(client)

        # Set up agents
        agent, multi_lingual_agent = setup_agents(client)

        # Run example queries
        run_example_queries(agent, multi_lingual_agent)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Clean up
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main() 