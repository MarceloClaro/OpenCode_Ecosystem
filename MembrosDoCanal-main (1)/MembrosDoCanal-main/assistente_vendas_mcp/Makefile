install:
	pip install -r requirements.txt

run:
	uvicorn server:app --reload --port 8000

client:
	python cliente_mcp.py

docker-build:
	docker build -t assistente-vendas-mcp .

docker-run:
	docker run -p 8000:8000 assistente-vendas-mcp

compose-up:
	docker-compose up --build

compose-down:
	docker-compose down