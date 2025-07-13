dev:
	npm run dev

logs:


dev-log: dev logs
# run with logs


build:

prod-run:
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker myapp:app