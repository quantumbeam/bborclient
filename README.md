
# BBO-Reitveld Python Client

A Python client library for the **[BBO-Reitveld](https://app.bborietveld.quantumbeam.org)**—a server designed to automate Rietveld analysis of powder X-ray diffraction (XRD) measurement data. This client offers a programmatic interface for synchronous communication with the server, allowing users to submit analysis jobs, monitor their progress, and retrieve results through code.


## ✨ Features

- Submit analysis tasks to the server for automated Reitveld refinements
- Download analysis results
- Create new user accounts


---

## 📦 Requirements

- Python 3.9 or higher
- Dependencies (automatically installed):
  - `requests`
  - `pydantic`
  - `python-abc`
  - `pandas` (optional, for getting Optuna data)
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
    measurementfile = '/path/xrd_data.csv',
    ciffiles = '/path/NaCl.cif',
    prmfile = '/path/XC-BB.instprm',
)

# Check progress of Study tasks
client.ask_task_queue_status(study_id)
```

#### Get results of analyses

```Python
from bbor_client import BBORClient
client = BBORClient('your_username', 'your_password')

# Get a Study
client.get_study(study_id)

# Get a list of all Studies of your group
client.find_studies()

# Get all Studies you performed
client.find_my_studies()

# Get Studies where study_name matches a specified pattern
pattern = '^hoge' # Use regular expression
query = {'study_name': {'$regex': pattern}}
client.find_studies(query)

# Get Studies of a specified structure model
query = {
  'samples': {
    '$elemMatch': {
      'phases': {
        '$elemMatch': {'name': 'Y2O3'}
      }
    }
  }
}
client.find_studies(query)

# Get Studies which started earlier than 3 days ago and later than 7 days ago
from datetime import datetime, timedelta, timezone
tz = timezone(timedelta(hours=9))
now = datetime.now(tz=tz).astimezone(timezone.utc)
threedaysago = now - timedelta(days=3)
sevendaysago = now - timedelta(days=7)
query = {
    'start_at': {
      '$lt': threedaysago.isoformat(),
      '$gt': sevendaysago.isoformat(),
    }
}
client.find_studies(query)

# Get a Trial
client.get_study(trial_id)

# Get all Trials of your group
client.find_trials()

# Get all Trials of a Study
client.get_study_trials(study_id)

# Get best Trials of a Study
client.get_best_trials(study_id)

# Get a Refine
client.get_refine(refine_id)

# Get all Refines of your group
client.find_refines()
```



## 🌈 Planned Features
- Implement the native methods of MongoDB such as find_one, aggregation pipeline, sort, projection.
- Limit (unintended) large-scale data requests





<!-- ## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

--- -->

## 📄 Terms and Conditions
TBD

## 🚘️ License

TBD
