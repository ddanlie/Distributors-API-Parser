### Local dev: 

- Install python 3.11+

- Install uv (fast python package manager)

 	**mac/linux**: `curl -LsSf https://astral.sh/uv/install.sh | sh`

	2. in folder with *pyproject.toml*: `uv sync --active -p /usr/bin/python3.13` - this will create `.venv` folder, use its python path in your IDE for syntax highlighting

- Install npm(node package manager) through nvm(node version manager) (for tailwindcss compilation) 

	**mac/linux**: 

	1. `curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash`
	2. nvm install node
	3. In folder with *package-lock.json*: `npm ci` (clean install)




- Logs are saved in scrapper.log.txt
- Run the project: `make dev`
- Build the project: `make build`


### Where to start from?

- Check architecture diagram
- `parser/core/endpoints.py` serves as entrypoint for users
- `endpoints.py` uses `parser/core/exec_manager.py` and its only public instance available
- We can also use `exec_manager` bypassing endpoints requests from `admin_service` folder
- General hierarchy: `main`->`core.endpoints`->`exec_manager`->`other "internal use" stuff`

### Docker dev (not ready):

1. Install `python` and `uv` (see **Local dev** above) for IDE syntax highlighting
2. In folder with Makefile Run `make docker-dev`

3. your "file explorer" `/parser` foler should be now synchronized with docker container folder for dynamic development.

 