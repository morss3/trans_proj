from core.settings import create_openrouter_model

llm = create_openrouter_model()
response = llm.invoke("Привет! Скажи одним предложением, кто ты.")
print(response.content)