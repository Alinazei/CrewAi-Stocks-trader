import os
import requests
import subprocess
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

def get_llm_config():
    """
    Get LLM configuration based on environment variables.
    Supports NVIDIA NIM API, Groq (cloud), and Ollama (local) models.
    """
    
    # Check if user wants to use NVIDIA NIM API
    use_nvidia_api = os.getenv("USE_NVIDIA_API", "false").lower() == "true"
    nvidia_api_key = os.getenv("NVIDIA_API_KEY")
    nvidia_api_base_url = os.getenv("NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1")
    nvidia_model = os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")
    nvidia_temperature = float(os.getenv("NVIDIA_TEMPERATURE", "0.3"))
    nvidia_top_p = float(os.getenv("NVIDIA_TOP_P", "0.7"))
    nvidia_max_tokens = int(os.getenv("NVIDIA_MAX_TOKENS", "4096"))  # Increased for better responses
    
    # Check if user wants to use Ollama (local models)
    ollama_model = os.getenv("OLLAMA_MODEL")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Check if user wants to use Groq (cloud API)
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    # Priority: NVIDIA > Groq > Ollama > Default
    if use_nvidia_api and nvidia_api_key:
        print(f"🚀 Using NVIDIA NIM API model: {nvidia_model}")
        
        # Additional parameters for NVIDIA API
        extra_params = {}
        if nvidia_model.startswith("qwen/"):
            # Add thinking mode for Qwen models
            extra_params["extra_body"] = {"chat_template_kwargs": {"thinking": True}}
        
        return LLM(
            model=nvidia_model,
            api_key=nvidia_api_key,
            base_url=nvidia_api_base_url,
            temperature=nvidia_temperature,
            top_p=nvidia_top_p,
            max_tokens=nvidia_max_tokens,
            timeout=120,  # Increased timeout for complex tasks
            max_retries=5,  # Increased retries
            **extra_params
        )
    elif groq_api_key:
        print("🌐 Using Groq cloud model: llama-3.3-70b-versatile")
        return LLM(
            model="groq/llama-3.3-70b-versatile",
            temperature=0.1,  # Slightly increased for better responses
            timeout=60,  # Increased timeout
            max_retries=5  # Increased retries
        )
    elif ollama_model:
        print(f"🤖 Using Ollama local model: {ollama_model}")
        return LLM(
            model=f"ollama/{ollama_model}",
            base_url=ollama_base_url,
            temperature=0.3,  # Balanced for stability and creativity
            timeout=120,  # Increased timeout for local models
            max_retries=5,  # Increased retries
            max_tokens=4096  # Increased token limit
        )
    else:
        print("⚠️  No LLM configuration found. Defaulting to Ollama with deepseek-r1:8b")
        print("💡 Make sure Ollama is running: ollama serve")
        return LLM(
            model="ollama/deepseek-r1:8b",
            base_url="http://localhost:11434",
            temperature=0.3,  # Balanced for stability and creativity
            timeout=120,  # Increased timeout for local models
            max_retries=5,  # Increased retries
            max_tokens=4096  # Increased token limit
        )


def verify_ollama_connection():
    """
    Verify that Ollama is running and accessible.
    """
    
    try:
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            available_models = [model["name"] for model in models]
            print(f"✅ Ollama is running. Available models: {available_models}")
            return True
        else:
            print(f"❌ Ollama responded with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False


def list_available_models():
    """
    List all available models in Ollama.
    """
    
    try:
        ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.get(f"{ollama_base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print("🤖 Available Ollama models:")
            for model in models:
                print(f"  - {model['name']} (Size: {model.get('size', 'Unknown')})")
            return [model["name"] for model in models]
        else:
            print("❌ Could not retrieve model list from Ollama")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return []


def download_model(model_name):
    """
    Download a model using Ollama.
    """
    
    try:
        print(f"📥 Downloading {model_name}...")
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Successfully downloaded {model_name}")
            return True
        else:
            print(f"❌ Failed to download {model_name}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ Download timeout for {model_name}")
        return False
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return False


# Recommended models for trading tasks
RECOMMENDED_MODELS = {
    "deepseek-r1:8b": {
        "description": "DeepSeek R1 8B - Excellent reasoning capabilities",
        "size": "~4.9GB",
        "best_for": "Complex analysis and reasoning tasks"
    },
    "llama3:8b": {
        "description": "Meta Llama 3 8B - Well-rounded performance",
        "size": "~4.7GB", 
        "best_for": "General purpose tasks"
    },
    "mistral:7b": {
        "description": "Mistral 7B - Fast and efficient",
        "size": "~4.1GB",
        "best_for": "Quick responses and basic analysis"
    },
    "gemma2:9b": {
        "description": "Google Gemma 2 9B - Good for structured tasks",
        "size": "~5.4GB",
        "best_for": "Structured analysis and reporting"
    }
}


def setup_ollama_for_trading():
    """
    Interactive setup for Ollama with recommended models for trading.
    """
    print("🚀 Setting up Ollama for Stock Trading")
    print("=" * 50)
    
    # Check if Ollama is running
    if not verify_ollama_connection():
        print("\n💡 To start Ollama, run: ollama serve")
        return False
    
    # List available models
    available_models = list_available_models()
    
    # Show recommended models
    print("\n📋 Recommended models for trading tasks:")
    for model_name, info in RECOMMENDED_MODELS.items():
        status = "✅ Installed" if model_name in available_models else "❌ Not installed"
        print(f"  {model_name}: {info['description']} ({info['size']}) - {status}")
    
    # Check if DeepSeek-R1:8b is available
    if "deepseek-r1:8b" not in available_models:
        print(f"\n📥 DeepSeek-R1:8b is not installed. This model is recommended for trading tasks.")
        download_choice = input("Would you like to download it now? (y/n): ").lower()
        if download_choice == 'y':
            download_model("deepseek-r1:8b")
        else:
            print("💡 You can download it later with: ollama pull deepseek-r1:8b")
    
    return True


if __name__ == "__main__":
    setup_ollama_for_trading() 