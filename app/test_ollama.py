from ollama import Client

def test_ollama():
    client = Client()
    try:
        response = client.generate(model="llama3.2:latest", prompt="Hello, how are you?")
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_ollama()
