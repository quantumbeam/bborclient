MB = 1024*1024

# BBOR Client configuration parameters
MAX_STUDY_NAME_LENGTH:int = 500
MIN_STUDY_NAME_LENGTH:int = 1
DEFAULT_N_TRIALS_TOTAL : int = 200
MAX_N_TRIALS_TOTAL : int = 10000
MAX_RANDOM_SEED:int = 10000
MAX_FILE_NAME_LENGTH:int = 256
MAX_FILE_SIZE:int = 1*MB
MAX_MEAS_FILESIZE:int = 10*MB

# GSAS-II specific constants
MFILE_SUFFIXES = ('.csv',)
PRM_SUFFIXES = ('.prm', '.instprm')
CIF_SUFFIXES = ('.cif', )

# Server
# SERVER_ADDRESS = '163.220.177.105'
SERVER_ADDRESS = 'api.bborietveld.quantumbeam.org'
API_URL_MDX = f'https://{SERVER_ADDRESS}'
API_URL_LOCAL = 'http://localhost:8000'
API_URL_DOCKER = 'http://bborapi:8000'
VERIFY_CERT = True
