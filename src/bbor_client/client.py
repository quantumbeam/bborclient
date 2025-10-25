import json
from pydantic import FilePath
from typing import Optional, Literal, Union
from pathlib import Path
import requests
from requests.models import Response
from .params.post_study.client import PostStudyClientParams
from .params.post_study.server import PostStudyServerParams
from .models.user import UserResponse as User
# from .models.study import Study
from .conf import VERIFY_CERT
from .util import api_url, require_token
from .parsers import selector


class BBORClient:
    def __init__(
            self,
            username: Optional[str] = None,
            password: Optional[str] = None,
            server: Literal['mdx', 'local', 'docker', 'dev'] = 'mdx',
            _dp = None,
    ):
        # Initialization
        self.server = server
        self._dp = _dp
        self.history: list = []
        self.prmlist = []
        self.ciflist = []
        self.seqlist = []


        if username is not None and password is not None:
            self.get_token(username, password)
        elif username is not None and password is not None:
            print('Both username and password are required for token generation')
            print('Token is not generated')
            self.token = None
        else:
            self.token = None

    def send_api(
            self,
            endpoint: str = '/',
            method: Literal['get','post','delete','put'] = 'get',
            params: Optional[dict] = None,
            data: Optional[dict] = None,
            json: Optional[dict] = None,
            files: Optional[list[tuple]] = None,
            header: Optional[dict] = None,
            authorization: bool = False,
    ) -> Response:
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        url = api_url(self.server, self._dp) + endpoint
        if authorization:
            if self.token is None:
                raise ValueError('Token is empty')
            if header:
                header.update({'Authorization': f'Bearer {self.token}'})
            else:
                header = {'Authorization': f'Bearer {self.token}'}
        if method=='get':
            response = requests.get(url, params=params, files=files, headers=header, verify=VERIFY_CERT)
        elif method=='post':
            response = requests.post(url, params=params, data=data, json=json, files=files, headers=header, verify=VERIFY_CERT)
        elif method=='delete':
            response = requests.delete(url, data=data, params=params, files=files, headers=header, verify=VERIFY_CERT)
        elif method=='put':
            response = requests.put(url, data=data, params=params, files=files, headers=header, verify=VERIFY_CERT)
        return response

    @require_token
    def get_me(
        self,
        return_dict: bool = False,
        return_response: bool = False,
    ) -> Union[User, Response, dict, None]:
        response = self.send_api(
            endpoint = '/user/me',
            method = 'get',
            authorization = True,
        )
        if response.status_code == 200:
            self.me = User.model_validate(response.json())
            if return_dict:
                return response.json()
            else:
                return User.model_validate(response.json())
        else:
            print('Request failed', response.content)
            self.me = None
            if return_response:
                return response

    @require_token
    def update_client_params(
        self,
        update_me: bool = True,
        update_prmlist: bool = True,
        update_ciflist: bool = True,
        update_seqlist: bool = True,
    ):
        ''' Synchronize client parameters with the server.'''
        if update_me:
            _ = self.get_me()
        if update_prmlist:
            _ = self.get_prm_list()
        if update_ciflist:
            _ = self.get_cif_list()
        if update_seqlist:
            _ = self.get_sequence_list()

    def get_token(
        self,
        username: str,
        password: str,
        return_response: bool = False,
    ) -> Optional[Response]:
        '''
        Get a token from the server. Also, get me, prmlist, ciflist.
        '''
        response = self.send_api(
            endpoint = '/token',
            method = 'post',
            data = {
                'username':username,
                'password':password,
            },
        )
        if response.status_code == 200:
            self.token = response.json()['access_token']
            print('Token received successfully')
            self.update_client_params()
        else:
            self.token = None
            print('Failed in getting a token')
            print(f'{response.status_code}: {response.content.decode()}')
        if return_response:
            return response

    def create_user(
            self,
            username: str,
            password: str,
            group_id: str,
            return_response: bool = False,
    ) -> Optional[Response]:
        data = dict(
            name = username,
            pwd = password,
            pwd2 = password,
            group = str(group_id),
        )
        response = self.send_api(
            endpoint = '/user',
            method = 'post',
            params = data,
        )
        if response.status_code == 200:
            print(f'User created successfully. Please make sure to store the password securely.')
            self.get_token(username, password)
        else:
            print('Request failed')
            print(f'{response.status_code}: {response.content.decode()}\n')
        if return_response:
            return response

    @require_token
    def get_prm_list(
        self,
        return_response: bool = False,
    ) -> Union[list[str], Response, None]:
        response = self.send_api(
            endpoint = 'file/prm',
            method = 'get',
            authorization = True,
        )
        if response.status_code==200:
            self.prmlist = json.loads(response.content)
            PostStudyServerParams.prm_file_list = self.prmlist
            print('prmlist updated')
            return self.prmlist
        else:
            if return_response:
                return response

    @require_token
    def upload_prm(
        self,
        file: FilePath,
        overwrite: bool = False,
        return_response: bool = False,
    ):
        file = Path(file)
        assert file.is_file()
        with file.open(mode='r+b') as f:
            response = self.send_api(
                endpoint = 'file/prm',
                method = 'post',
                files = [('files', f)],
                params = dict(overwrite=overwrite),
                authorization = True,
            )
        if response.status_code==200:
            print(json.loads(response.content))
            _ = self.get_prm_list(return_response=False)
        if return_response:
            return response

    @require_token
    def delete_prm(
        self,
        filenames: Union[list[str], str],
        ignore_absent_files: bool = True,
        return_response: bool = False,
    ):
        if isinstance(filenames, str):
            filenames = [filenames]
        for file in filenames:
            if file not in self.prmlist:
                if ignore_absent_files:
                    print(f'{file} not found in the server. Skipped.')
                    continue
                else:
                    raise ValueError(f'{file} not found in the server')
        response = self.send_api(
            endpoint = 'file/prm',
            method = 'delete',
            params = dict(filenames=filenames),
            authorization = True,
        )
        if response.status_code==200:
            print(json.loads(response.content))
        else:
            print('Request failed')
        _ = self.get_prm_list()
        if return_response:
            return response


    @require_token
    def get_cif_list(
        self,
        return_response: bool = False,
    ) -> Union[list[str], Response, None]:
        response = self.send_api(
            endpoint = 'file/cif',
            method = 'get',
            authorization = True,
        )
        if response.status_code==200:
            self.ciflist = json.loads(response.content)
            PostStudyServerParams.cif_file_list = self.ciflist
            print('ciflist updated')
            return self.ciflist
        else:
            if return_response:
                return response

    @require_token
    def upload_cif(
        self,
        file: FilePath,
        overwrite: bool = False,
        return_response: bool = False,
    ):
        file = Path(file)
        assert file.is_file()
        with file.open(mode='r+b') as f:
            response = self.send_api(
                endpoint = 'file/cif',
                method = 'post',
                files = [('files', f)],
                params = dict(overwrite=overwrite),
                authorization = True,
            )
        if response.status_code==200:
            print(json.loads(response.content))
            _ = self.get_cif_list(return_response=False)
        if return_response:
            return response

    @require_token
    def delete_cif(
        self,
        filenames: Union[list[str], str],
        ignore_absent_files: bool = True,
        return_response: bool = False,
    ):
        if isinstance(filenames, str):
            filenames = [filenames]
        for file in filenames:
            if file not in self.prmlist:
                if ignore_absent_files:
                    print(f'{file} not found in the server. Skipped.')
                    continue
                else:
                    raise ValueError(f'{file} not found in the server')
        response = self.send_api(
            endpoint = 'file/cif',
            method = 'delete',
            params = dict(filenames=filenames),
            authorization = True,
        )
        if response.status_code==200:
            print(json.loads(response.content))
        else:
            print('Request failed')
        _ = self.get_cif_list()
        if return_response:
            return response


    @require_token
    def get_sequence_list(
        self,
        return_response: bool = False,
    ):
        response = self.send_api(
            endpoint = 'file/seq',
            method = 'get',
            authorization = True,
        )
        if response.status_code==200:
            self.seqlist = json.loads(response.content)
            print('seqlist updated')
            PostStudyServerParams.sequence_list = self.seqlist
            return json.loads(response.content)
        else:
            if return_response:
                return response

    @require_token
    def upload_seq(
        self,
        file: FilePath,
        overwrite: bool = False,
        return_response: bool = False,
    ):
        file = Path(file)
        assert file.is_file()
        with file.open(mode='r+b') as f:
            response = self.send_api(
                endpoint = 'file/seq',
                method = 'post',
                files = [('files', f)],
                params = dict(overwrite=overwrite),
                authorization = True,
            )
        if response.status_code==200:
            print(json.loads(response.content))
            _ = self.get_cif_list(return_response=False)
        if return_response:
            return response

    @require_token
    def delete_seq(
        self,
        filenames: Union[list[str], str],
        ignore_absent_files: bool = True,
        return_response: bool = False,
    ):
        if isinstance(filenames, str):
            filenames = [filenames]
        for file in filenames:
            if file not in self.prmlist:
                if ignore_absent_files:
                    print(f'{file} not found in the server. Skipped.')
                    continue
                else:
                    raise ValueError(f'{file} not found in the server')
        response = self.send_api(
            endpoint = 'file/seq',
            method = 'delete',
            params = dict(filenames=filenames),
            authorization = True,
        )
        if response.status_code==200:
            print(json.loads(response.content))
        else:
            print('Request failed')
        _ = self.get_sequence_list()
        if return_response:
            return response


    @require_token
    def _post_study_task(
        self,
        **kwargs,
    ) -> Response:
        ''' Used internally from client and from the web app'''
        # Parse the measurement file if provided
        if kwargs.get('gpxfile'):
            m_parser = None
        elif kwargs.get('measurementfile'):
            parser = selector(
                filename = kwargs['measurementfile'].name,
            )
            m_parser = parser(filepath=kwargs['measurementfile'])
        elif kwargs.get('measurement_filename') and kwargs.get('measurement_filecontent'):
            parser = selector(
                filename = kwargs['measurement_filename'],
            )
            m_parser = parser(
                filename=kwargs['measurement_filename'],
                filecontent = kwargs['measurement_filecontent'],
            )
        else:
            m_parser = None

        # Validate the arguments with Server Parameter model
        server_side_arg_model = PostStudyServerParams.model_validate(
            kwargs | dict( #Overwrite the following keys in kwargs
                measurement_filecontent = m_parser._to_csv_bytesio() if m_parser else None,
                measurement_filename = m_parser.csvname if m_parser else None,
            )
        )

        # From Server Parameter model to request parameters
        s = server_side_arg_model
        data = s.model_dump()
        files = []
        if s.measurement_filecontent:
            files.append(
                ('files', (s.measurement_filename, s.measurement_filecontent))
            )

        response = self.send_api(
            endpoint = '/task/study',
            method = 'post',
            data = data,
            files = files,
            authorization = True,
        )
        return response

    @require_token
    def post_bborietveld_study_task(
        self,
        return_response: bool = False,
        **kwargs,
    ) -> Optional[Response]:
        '''Used from client'''
        # Validate with Client Parameter model and do some preprocessing
        client_interface_arg_model = PostStudyClientParams.model_validate(kwargs)
        c = client_interface_arg_model

        # Upload files if necessary
        if c.prmfile:
            self.upload_prm(c.prmfile, overwrite=c.overwrite_prmfile)
        if c.ciffiles:
            for ciffile in c.ciffiles:
                self.upload_cif(ciffile, overwrite=c.overwrite_ciffiles)

        # Post the study task
        response = self._post_study_task(
            **c.model_dump(),
            measurement_filecontent = c.measurementfile.read_bytes() if c.measurementfile else None,
            measurement_filename = c.measurementfile.name if c.measurementfile else None,
        )

        if response.status_code == 202:
            # print('Request successful')
            print(f'{response.json()}')
            study_id = response.json()['study_id']
            self.history.append(study_id)
        else:
            print('Request failed')
            print(f'{response.status_code}: {response.content.decode()}')
        if return_response:
            return response


    @require_token
    def ask_task_queue_status(
        self,
        study_id: Optional[str] = None,
        return_response: bool = False,
    ) -> Union[dict, None, Response]:
        if study_id is not None:
            param = {'study_id': study_id}
        else:
            param = None
        response = self.send_api(
            endpoint = '/task/status',
            method = 'get',
            params = param,
            authorization = True,
        )
        if response.status_code==200:
            return response.json()
        else:
            print('Request failed')
            print(f'{response.status_code}: {response.content.decode()}')
            if return_response:
                return response
            return None

    # @require_token
    # def get_study(
    #     self,
    #     study_id:str,
    #     return_dict: bool = False,
    #     return_response: bool = False,
    # ) -> Union[Study, dict, None, requests.models.Response]:
    #     response =  self.send_api(
    #         endpoint = '/study',
    #         method = 'get',
    #         params = {'study_id': str(study_id)},
    #         authorization = True,
    #     )
    #     if response.status_code==200:
    #         if return_dict:
    #             return response.json()
    #         else:
    #             return Study.model_validate(response.json())
    #     else:
    #         print('Request failed')
    #         print(f'{response.status_code}: {response.content.decode()}')
    #         if return_response:
    #             return response

