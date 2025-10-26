import os
import shutil
import json
import tempfile
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

orgins=["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CURRENT_PROJECT_DIR = None

class Query(BaseModel):
    query: str

def enter(state: str):
    os.environ["GOOGLE_API_KEY"] = "AIzaSyB49t1RsKBrFM5NHM-M3O6pl4ljA8U4_60"  # Make sure this is correct

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0)
    
    prompt = ChatPromptTemplate.from_template(
        f"""
        You are a code generation bot. Based on the query '{state}', generate the appropriate project structure and code files in JSON format.
        The project could be a frontend, backend, or full-stack application, and could be developed using different frameworks such as FastAPI, Spring Boot, React, or basic HTML, CSS, and JavaScript. 
        
        **Instructions**:
        - If the query asks for a **frontend project**, generate HTML, CSS, and JS files.
        - If the query asks for a **backend project**, generate either a FastAPI or Spring Boot setup.
        - If the query asks for a **full-stack project**, generate both frontend and backend structures accordingly.
        - Output should not include any greetings or explanations, only the project structure in JSON format.

        **Format**:
       
            "instruction": [
                ["Project"],
                ["Project", "frontend"],
                ["Project", "frontend", "index.html"],
                ["Project", "frontend", "style.css"],
                ["Project", "frontend", "script.js"]
            ],
            "files": 
                "index.html": "<html><body>...</body></html>",
                "style.css": "body ",
                "script.js": "console.log('Hello world');"
          

        **Important**:
        - If the project is **backend** (FastAPI or Spring Boot), generate Python or Java files with necessary configurations.
        - If the project is **full-stack**, generate both frontend and backend files.

        Respond only with the project structure and code, without any extra words.
        """
    )
    
   
    chain = prompt | llm
    response = chain.invoke({'query': state})
    
   
    return response

def create_files_from_structure(query: str):
    global CURRENT_PROJECT_DIR
    content = enter(query)
    content_string = content.content

    
    cleaned_content = content_string.strip("```json\n").strip("```")

    try:
        data = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Failed to parse JSON.")
    
    project_dir = tempfile.mkdtemp()
    logger.debug(f"Creating project files in {project_dir}")
    try:
        for path_parts in data['instruction']:
            path = os.path.join(project_dir, *path_parts)
            if '.' in path_parts[-1]:  # it's a file
                os.makedirs(os.path.dirname(path), exist_ok=True)
                filename = path_parts[-1]
                if filename in data['files']:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(data['files'][filename])
            else:
                os.makedirs(path, exist_ok=True)
        CURRENT_PROJECT_DIR = project_dir
        return project_dir
    except Exception as e:
        shutil.rmtree(project_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get-file-content")
async def get_file_content(query: Query):
    try:
        project_dir = create_files_from_structure(query.query)
        if not os.path.exists(project_dir):
            raise FileNotFoundError(f"The directory '{project_dir}' does not exist.")

        project_files = {}
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        project_files[file_path[len(project_dir)+1:]] = f.read()
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {str(e)}")
        return JSONResponse(content={"files": project_files})
    except Exception as e:
        logger.error(f"Error in get-file-content: {str(e)}")
        return JSONResponse(status_code=500, content={"message": str(e)})

@app.get("/download-project")
async def download_project(background_tasks: BackgroundTasks):
    global CURRENT_PROJECT_DIR
    if CURRENT_PROJECT_DIR is None or not os.path.exists(CURRENT_PROJECT_DIR):
        raise HTTPException(status_code=404, detail="No project available for download")

    zip_path_without_extension = os.path.join(CURRENT_PROJECT_DIR, "project_files")
    shutil.make_archive(zip_path_without_extension, 'zip', root_dir=CURRENT_PROJECT_DIR)
    zip_path = f"{zip_path_without_extension}.zip"

    if not os.path.exists(zip_path):
        raise HTTPException(status_code=500, detail="ZIP file creation failed")

    def cleanup():
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            if os.path.exists(CURRENT_PROJECT_DIR):
                shutil.rmtree(CURRENT_PROJECT_DIR)
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")

    background_tasks.add_task(cleanup)

    return FileResponse(
        zip_path,
        media_type='application/zip',
        headers={"Content-Disposition": "attachment; filename=project_files.zip"}
    )
