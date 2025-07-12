from fastapi import FastAPI
app = FastAPI()


#TODO: 
# Crucial:
# Bitrix authentication integration
# Set up nginx public folder
# Close 8000 port (access to this app should be only using nginx)
# Define requests limitations
# Define roles: e.g. only admin can send Purchase Orders, See invoices
# Define tech stack: nginx, uvicorn, python(version?) fastapi, tailwind, jinja2, axios 

# Architecture
# Define abstract distributor client, create class for every distributor api
# Unify distributor filters - if clients share some filters we can compare them, if not - find out how to show them

# Code notes
# HTML Routing: <a href="/route"> <button> Go there </button> </a>

#Bitrix sends post request 
#with credentials when app is opened
@app.post("/")
def read_root():
    return "<h1>Hello, World!</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)