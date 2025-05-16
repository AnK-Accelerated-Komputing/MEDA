# MEDA

A multi-agent system for parametric CAD model creation

## Setup Instructions

#### Installation Steps

#### Using Conda

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AnK-Accelerated-Komputing/MEDA.git
   cd MEDA
   ```

2. **Create and Activate Conda Environment**
   ```bash
   conda env create -f environment.yml
   conda activate MEDA
   ```
#### Using Pip

1. **Clone the Repository**
   ```bash
   git clone https://github.com/AnK-Accelerated-Komputing/MEDA.git
   cd MEDA
   ```

2. **Create and Activate a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

### Common Steps for Both Environments

3. **Set Environment Variables**
   Create a `.env` file in the root directory with the following content:
   ```env
   GEMINI_API_KEY='your_gemini_api_key'
   GROQ_API_KEY='your_groq_api_key'
   AZURE_API_KEY='your_azure_api_key'
   AZURE_OPENAI_BASE='your_azure_openai_base_url'
   ```

   Alternatively, you can export them directly in your shell:
   ```bash
   export GEMINI_API_KEY='your_gemini_api_key'
   export GROQ_API_KEY='your_groq_api_key'
   export AZURE_API_KEY='your_azure_api_key'
   export AZURE_OPENAI_BASE='your_azure_openai_base_url'
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```


3. **Set Environment Variables**
   Create a `.env` file in the root directory with the following content:
   ```env
   GEMINI_API_KEY='your_gemini_api_key'
   GROQ_API_KEY='your_groq_api_key'
   AZURE_API_KEY='your_azure_api_key'
   AZURE_OPENAI_BASE='your_azure_openai_base_url'
   ```

   Alternatively, you can export them directly in your shell:
   ```bash
   export GEMINI_API_KEY='your_gemini_api_key'
   export GROQ_API_KEY='your_groq_api_key'
   export AZURE_API_KEY='your_azure_api_key'
   export AZURE_OPENAI_BASE='your_azure_openai_base_url'
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```
   For streamlit app
   ```bash
   streamlit run streamlitapp.py
   ```
   You can insert the api key for different models with streamlit app.

5. **Interact with the Application**
   Follow the on-screen instructions to interact with MEDA.

### Notes

- Ensure all environment variables are set correctly to avoid runtime errors.
- If you encounter any issues, check the dependencies and ensure all are installed correctly.


## FAQ

#### How to check the install packages?

```bash
pip list
```

#### How to verify the installion?

```bash
pip show <package_name>
```

#### If error occur during Installation?

Make sure your pip and setuptools are up to date by executing command: :

```bash
pip install --upgrade pip setuptools

```

#### Dependency conflict between the installed version of package?

##### Example Error: : installing collected packages: numpy

ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
nlopt 2.8.0 requires numpy<3,>=2, but you have numpy 1.26.4 which is incompatible.

Solution: Uninstall and reinstall with compatible versions. For example:
To installs a specific version of the package (e.g., numpy==1.24.0).

```bash
pip uninstall -y numpy && pip install numpy==1.24.0
```

Replace <conflict_package_name> with the actual package name and <replace_your_required_version> with the version that matches the requirements of other packages in your project.

```bash
pip uninstall -y <conflict_package_name> && pip install <conflict_package_name>==<replace_your_required_version>
```