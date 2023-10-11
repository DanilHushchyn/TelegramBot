import httpx

client = httpx.Client(verify=False)
resp = client.get("http://127.0.0.1:8000/api/v1/auth/login/")
print(resp)