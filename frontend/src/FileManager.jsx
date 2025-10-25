import React, { useState } from "react";
import axios from "axios";

function FileManager() {
  const [fileName, setFileName] = useState("");
  const [fileContent, setFileContent] = useState("");

  const handleCreateFile = async () => {
    try {
      const response = await axios.post("http://localhost:8000/create-file", {
        name: fileName,
        content: fileContent,
      });
      alert(response.data.status);  // Show a success message
    } catch (error) {
      console.error("Error creating file:", error);
    }
  };

  const handleDownloadProject = async () => {
    try {
      const response = await axios.get("http://localhost:8000/download-project", {
        responseType: "blob",
      });

      const link = document.createElement("a");
      link.href = URL.createObjectURL(response.data);
      link.download = "project.zip";
      link.click();
    } catch (error) {
      console.error("Error downloading project:", error);
    }
  };

  return (
    <div>
      <h2>Create File</h2>
      <input
        type="text"
        placeholder="File Name"
        value={fileName}
        onChange={(e) => setFileName(e.target.value)}
      />
      <textarea
        placeholder="File Content"
        value={fileContent}
        onChange={(e) => setFileContent(e.target.value)}
      />
      <button onClick={handleCreateFile}>Create File</button>

      <h2>Download Project</h2>
      <button onClick={handleDownloadProject}>Download Project as ZIP</button>
    </div>
  );
}

export default FileManager;
