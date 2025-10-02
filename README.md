
# BBO-Reitveld Python Client

A Python client library for the **[BBO-Reitveld](https://app.bborietveld.quantumbeam.org)**—a server designed to automate Rietveld analysis of powder X-ray diffraction (XRD) measurement data. This client offers a programmatic interface for synchronous communication with the server, allowing users to submit analysis jobs, monitor their progress, and retrieve results through code.


## ✨ Features

- Submit analysis tasks to the server for automated Reitveld refinements
- Create new user accounts
- Results and resources are shared among and closed to Group members


---

## 📦 Requirements

- Python 3.9 or higher
- Dependencies (automatically installed):
  - `requests`
  - `pandas`
  - `pydantic`
  - `python-abc`
  - `parsexml` (optional, for parsing XML type measurement file)

---

## 🚀 Installation

Install directly from the GitHub repository:

```bash
pip install git+https://git@github.com:quantumbeam/bborclient.git
```

---

## ⚡ Usage
#### Create an account
```Python
from bbor_client import BBORClient
client = BBORClient()
client.create_user(
    username = 'your_username',
    password = 'your_password',
    group_id = 'your_group_id',
)
```

#### Start a Study of BBO-Rietveld analysis
```Python
from bbor_client import BBORClient
client = BBORClient('your_username', 'your_password')

# Start a BBO-Rietveld study
client.post_bborietveld_study_task(
    study_name_base = 'study_name',
    measurementfile = 'xrd_data.csv',
    ciffiles = 'NaCl.cif',
    prmfile = 'PXC-BB.instprm',
)

# Check progress of a Study
client.ask_task_queue_status(study_id)
```

<!-- #### Get results of analyses

```Python
from bbor_client import BBORClient
client = BBORClient('your_username', 'your_password')

# Get a result of a Study
client.get_study(study_id)

# Get a list of Study IDs of your group
client.find_study()

# Get a list of Study IDs you performed
client.find_study()

``` -->


<!-- ## 🧪 API Reference

| Method | Description |
|--------|-------------|
| `register(username, password)` | Create a new user account |
| `login(username, password)` | Authenticate and store token |
| `submit_analysis(file_path)` | Submit an XRD file for analysis |
| `check_progress(job_id)` | Check the status of a submitted job |
| `download_results(job_id, output_dir)` | Download results to a local directory |
--- -->


## 🌈 Planned Features
- Download analysis results






<!-- ## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

--- -->

## 📄 Terms and Conditions
TBD

## 🚘️ License

TBD
