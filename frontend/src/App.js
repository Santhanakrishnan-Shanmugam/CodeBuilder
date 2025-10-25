import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [files, setFiles] = useState({}); 
  const [zipUrl, setZipUrl] = useState(""); 
  const[query,setQuery]=useState("");

  
  
  const fetchFiles = async () => {
    try {
      const payload={query:query}
      const response = await axios.post("http://localhost:8000/get-file-content",payload);
      setFiles(response.data.files); 
    } catch (error) {
      console.error("Error fetching project files:", error);
    }
  };

  
  const handleDownload = async () => {
    try {
      const response = await axios.get("http://localhost:8000/download-project", {
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "project_files.zip");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error("Error downloading project:", error);
    }
  };

  return (
    <div className="App">
      <div className="form-container">
        <h1 className="title">Code Builder</h1>
        <input  className="textfeild" type="text" placeholder="Describe your software" onChange={(e)=>{setQuery(e.target.value)}}></input>
        
        <button onClick={fetchFiles} className="submit-btn">
          Show Project Files
        </button>
      </div>

      
      {Object.keys(files).length > 0 && (
        <div className="file-manager-container">
          <div className="file-manager">
            <h3>File Structure</h3>
            {Object.keys(files).map((fileName) => (
              <div key={fileName}>
                <strong>{fileName}</strong>
                <pre>{files[fileName]}</pre>
              </div>
            ))}
          </div>

          
          <button onClick={handleDownload} className="download-btn">
            Download Project Zip
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
