import os
from dotenv import load_dotenv
from aiohttp import web
from ragtools import attach_rag_tools
from rtmt import RTMiddleTier
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential

if __name__ == "__main__":
    # Load environment variables from a .env file
    load_dotenv()
    
    # Retrieve configuration values from environment variables
    llm_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
    search_endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    search_index = os.environ.get("AZURE_SEARCH_INDEX")
    search_key = os.environ.get("AZURE_SEARCH_API_KEY")

    # Determine the credentials to use for Azure services
    credentials = DefaultAzureCredential() if not llm_key or not search_key else None

    # Create an aiohttp web application
    app = web.Application()

    # Initialize the RTMiddleTier with the endpoint and credentials
    rtmt = RTMiddleTier(llm_endpoint, AzureKeyCredential(llm_key) if llm_key else credentials)
    
    # Set the system message for the RTMiddleTier
    rtmt.system_message = (
        "You are a helpful assistant. The user is listening to answers with audio, so it's *super* important that answers are as short as possible, a single sentence if at all possible. "
        "Use the following step-by-step instructions to respond with short and concise answers using a knowledge base: "
        "Step 1 - Always use the 'search' tool to check the knowledge base before answering a question. "
        "Step 2 - Always use the 'report_grounding' tool to report the source of information from the knowledge base. "
        "Step 3 - Produce an answer that's as short as possible. If the answer isn't in the knowledge base, say you don't know."
    )
    
    # Attach RAG tools to the RTMiddleTier
    attach_rag_tools(rtmt, search_endpoint, search_index, AzureKeyCredential(search_key) if search_key else credentials)

    # Attach the RTMiddleTier to the aiohttp web application
    rtmt.attach_to_app(app, "/realtime")

    # Add routes to serve the static index.html file and static assets
    app.add_routes([web.get('/', lambda _: web.FileResponse('./static/index.html'))])
    app.router.add_static('/', path='./static', name='static')
    
    # Run the aiohttp web application on localhost at port 8765
    web.run_app(app, host='localhost', port=8765)