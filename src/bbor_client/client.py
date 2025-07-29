import json
from pydantic import FilePath
from typing import Optional, Literal, Union
from pathlib import Path
import requests
from requests.models import Response
from .params.post_study.client import PostStudyClientParams
from .params.post_study.server import PostStudyServerParams
from .models.user import UserResponse as User
from .conf import API_URL_MDX, API_URL_DOCKER, API_URL_LOCAL, VERIFY_CERT
from .util import api_url, require_token


class BBORClient:
    def __init__(
            self,
            username: Optional[str] = None,
            password: Optional[str] = None,
            server: Literal['mdx', 'local', 'docker'] = 'mdx',
    ):
        # Initialization
        self.server = server
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
        url = api_url(self.server) + endpoint
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
            if return_response:
                return response

    def get_token(
        self,
        username: str,
        password: str,
        return_response: bool = False,
    ) -> Optional[Response]:
        '''
        Get a token from the server. Also, get me, prmlist, ciflist.
        '''
        credentials = {
            'username':username,
            'password':password,
            }
        response = self.send_api(
            endpoint = '/token',
            method = 'post',
            data = credentials,
        )
        if response.status_code == 200:
            self.token = response.json()['access_token']
            print('Token received successfully')
            _ = self.get_me()
            _ = self.get_prm_list()
            _ = self.get_cif_list()
            _ = self.get_sequence_list()
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
            print(f'User created successfully')
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
            PostStudyClientParams.prm_file_list = self.prmlist
            print('self.prmlist updated')
            return self.prmlist
        else:
            if return_response:
                return response

    @require_token
    def upload_prm(
        self,
        prmfile: FilePath,
        overwrite: bool = False,
        return_response: bool = False,
    ):
        if isinstance(prmfile, str):
            prmfile = Path(prmfile)
        assert prmfile.is_file()
        response = self.send_api(
            endpoint = 'file/prm',
            method = 'post',
            files = [('files', prmfile.open(mode='r'))],
            params = dict(overwrite=overwrite),
            authorization = True,
        )
        if response.status_code==200:
            print(json.loads(response.content))
            _ = self.get_prm_list(return_response=False)
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
            PostStudyClientParams.cif_file_list = self.ciflist
            print('self.ciflist updated')
            return self.ciflist
        else:
            if return_response:
                return response

    @require_token
    def upload_cif(
        self,
        ciffile: FilePath,
        overwrite: bool = False,
        return_response: bool = False,
    ):
        if isinstance(ciffile, str):
            ciffile = Path(ciffile)
        assert ciffile.is_file()
        response = self.send_api(
            endpoint = 'file/cif',
            method = 'post',
            files = [('files', ciffile.open(mode='r'))],
            params = dict(overwrite=overwrite),
            authorization = True,
        )
        if response.status_code==200:
            print(json.loads(response.content))
            _ = self.get_cif_list(return_response=False)
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
            print('self.seqlist updated')
            return json.loads(response.content)
        else:
            if return_response:
                return response


    @require_token
    def post_bborietveld_study_task(
        self,
        return_response: bool = False,
        **kwargs,
    ) -> Optional[Response]:
        # First validation from client interface and some data processing
        client_interface_arg_model = PostStudyClientParams.model_validate(**kwargs)
        # Second validation to create the argument model
        server_side_arg_model = PostStudyServerParams.model_validate(
            **client_interface_arg_model.model_dump(),
            
        )
        # Upload files if necessary
        if client_interface_arg_model.prmfile:
            self.upload_prm(client_interface_arg_model.prmfile, overwrite=True)


        data = server_side_arg_model.model_dump()

        if arg_model.resume_study:
            files = []
        elif arg_model.inputdir:
            files = [
                ('files', open(file, 'rb'))
                for file in iglob(os.path.join(arg_model.inputdir, '*')) # type: ignore
            ]
        elif arg_model.gpxfile:
            files = [
                ('files', open(arg_model.gpxfile, 'rb'))
            ]
        elif arg_model.mfile is not None and arg_model.ciffiles is not None and arg_model.prmfile is not None:
            files = [
                ('files', open(arg_model.mfile, 'rb')),
                ('files', open(arg_model.prmfile, 'rb')),
            ]
            files.extend([
                ('files', open(cif, 'rb')) for cif in arg_model.ciffiles
            ])
        else:
            raise Exception
        if arg_model.mysequencefile is not None:
            files.append(
                ('files', open(arg_model.mysequencefile, 'rb'))
            )
        
        # if self.token:
        #     header = {'Authorization': f'Bearer {self.token}'}
        # else:
        #     raise ValueError ('token is empty')
        
        # url = api_url(self.server)+'/task/study'

        response = self.send_api(
            endpoint = '/task/study',
            method = 'post',
            data = data,
            files = files,
            authorization = True,
        )
        # response = requests.post(
        #     url,
        #     data=data,
        #     files=files,
        #     headers=header,
        #     # allow_redirects=False,
        #     verify=VERIFY_CERT,
        # )

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


