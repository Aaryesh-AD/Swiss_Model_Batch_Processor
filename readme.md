# **Swiss-Model Batch Processor**
**Automate Multi-Target Homology Modeling Using a Single Template with SwissModel API**

## **Overview**
Swiss-Model Batch Processor is a **Python-based automation tool** designed to **batch submit multiple protein sequences** to **SwissModel** using a **single structural template**. This script simplifies high-throughput homology modeling by programmatically handling **job submissions, monitoring, and structured result retrieval**.

## **Features**
- **Batch Submission** – Automates SwissModel API requests for multiple sequences.  
- **Single Template Usage** – Models all targets against one specified template.  
- **Parallel Processing** – Uses multithreading for faster execution.  
- **Rate Limit Handling** – Prevents exceeding SwissModel’s API limits (100/min, 2000/6h).  
- **Structured Output Management** – Saves models in separate directories based on clusters.  
- **Separate PDB & CIF Outputs** – Organizes **PDB and CIF** files into dedicated subfolders. 
- **GUI Interface** - Provides a user-friendly GUI for easy usage. 

---

## **Installation**

### To use the GUI: 
### **Download the Executable** From the releases page:
- **Windows**: [Download](https://github.com/Aaryesh-AD/Swiss_Model_Batch_Processor/releases/download/v1.0.0/Swiss_Model_Batch_processor-v1.0.0-windows-x86_64.zip)
- **Linux**: [Download](https://github.com/Aaryesh-AD/Swiss_Model_Batch_Processor/releases/download/v1.0.0/Swiss_Model_Batch_processor-v1.0.0-linux-x86_64.tar.gz)

---

### **For the Python Script**

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/Aaryesh-AD/Swiss_Model_Batch_Processor.git
    cd Swiss_Model_Batch_Processor
    ```

2. **Install any required dependencies** (if not already installed).

---

## **Setup**

### **Step 1: Configure API Access**

SwissModel requires an **API Key** for authentication. Follow these steps:

1. Retrieve your **API Key/Token** from the [SwissModel Account Page](https://swissmodel.expasy.org/repository?query=token).
2. For the python CLI usage,  in the project directory, create a new file called `config.json` and add your API Key/Token:

   ```json
   {
       "API_KEY": "your_api_key_here"
   }
   ```
For the GUI, the API key can be entered directly in the GUI.

> **Tip:** Make sure `config.json` is kept secure and is not accidentally shared publicly.

---

### **Step 2: Prepare Your Input Files**

- **FASTA File:** A file containing the target sequences (in standard FASTA format) that you want to model.
- **Template PDB File:** The **single template** file (in PDB format) used as the structural basis for modeling all target sequences.

---

## **Usage**

There are two modes to run SwissBatchModeler: **GUI** and **Command-Line Interface (CLI)**.

### **Using the GUI**

- **On Windows:**  
  Double-click on the `Swiss-Modeler_Batch_Processor_GUI.exe` file.
  
- **On Linux:**  
  In the program directory, run:
  
  ```bash
  ./Swiss-Modeler_Batch_Processor_GUI
  ```

> The GUI provides an interactive interface for selecting input files, configuring options, and viewing progress.

---

### **Using the Python Script (CLI Mode)**

Run the script with the following command:

```bash
python SM_batch_processor.py <fasta_file> <template_pdb_file> <output_directory>
```

#### **Example:**

```bash
python SM_batch_processor.py input.fasta template.pdb results/
```

> **Note:** Ensure that the `config.json` file is located in the same directory as the script.

---

## **Output Structure**
Models are saved under `output_directory/` in organized folders:

```
results/
├── cluster_0_model/
│   ├── PDB/
│   │   ├── cluster_0_model_001.pdb
│   │   ├── cluster_0_model_002.pdb
│   ├── CIF/
│   │   ├── cluster_0_model_001.cif
│   │   ├── cluster_0_model_002.cif
├── cluster_1_model/
│   ├── PDB/
│   │   ├── cluster_1_model_001.pdb
│   ├── CIF/
│   │   ├── cluster_1_model_001.cif
│   └── ...
```

---

## **SwissModel API Details**
- **Authentication**: Requires an API token in headers (`Token {API_KEY}`).
- **Rate Limits**:
  - **Rapid Submission**: **100 requests/minute**
  - **Prolonged Submission**: **2000 requests/6 hours**
- **Endpoints**:
  - **Submit Job**: `POST https://swissmodel.expasy.org/user_template`
  - **Check Status**: `GET https://swissmodel.expasy.org/project/{project_id}/models/summary/`

---

## **Advanced Configuration**
Modify **batch settings** in `SM_batch_processor.py`:
```python
RAPID_RATE_LIMIT = 100  # Max 100 requests per minute
REQUEST_INTERVAL = 60   # 1-minute interval if rate is exceeded
MAX_WORKERS = 5         # Adjust thread count for parallel processing
```

---

## **License**
This project is licensed under the **MIT License**.

---

## **Contributions**
Contributions are welcome! To contribute:
1. Fork the repo.
2. Create a new branch (`feature-name`).
3. Commit changes and push.
4. Submit a pull request.

---

## **Contact**
For issues, please open a GitHub issue or contact **adeshpande334@gatech.edu**.

---
## References

1. **Waterhouse A, et al. (2018)**  
   *SWISS-MODEL: homology modelling of protein structures and complexes.*  
   Nucleic Acids Res 46, W296-W303.  
   [PubMed](https://pubmed.ncbi.nlm.nih.gov/29788355) | [DOI](https://doi.org/10.1093/nar/gky427)

2. **Bienert S, et al. (2017)**  
   *The SWISS-MODEL Repository - new features and functionality.*  
   Nucleic Acids Res 45, D313-D319.  
   [PubMed](https://pubmed.ncbi.nlm.nih.gov/27899672) | [DOI](https://doi.org/10.1093/nar/gkw1132)

3. **Guex N, Peitsch MC, Schwede T (2009)**  
   *Automated comparative protein structure modeling with SWISS-MODEL and Swiss-PdbViewer: A historical perspective.*  
   Electrophoresis 30, S162-S173.  
   [PubMed](https://pubmed.ncbi.nlm.nih.gov/19517507) | [DOI](https://doi.org/10.1002/elps.200900140)

4. **Studer G, et al. (2020)**  
   *QMEANDisCo - distance constraints applied on model quality estimation.*  
   Bioinformatics 36, 1765-1771.  
   [PubMed](https://pubmed.ncbi.nlm.nih.gov/31697312) | [DOI](https://doi.org/10.1093/bioinformatics/btz828)

5. **Bertoni M, et al. (2017)**  
   *Modeling protein quaternary structure of homo- and hetero-oligomers beyond binary interactions by homology.*  
   Scientific Reports 7.  
   [PubMed](https://pubmed.ncbi.nlm.nih.gov/28874689) | [DOI](https://doi.org/10.1038/s41598-017-09654-8)

---
