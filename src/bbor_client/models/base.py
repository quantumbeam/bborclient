from pydantic import BaseModel, ConfigDict


class ClientModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        populate_by_name = True,
        str_max_length=1000,
        use_attribute_docstrings = True,
    )
    # def __repr__(self, depth=0):
    #     return repr_value(self, depth)
    def keys(self):
        return self.__dict__.keys()
    # @classmethod
    # def model_validate(cls, value, *arg, **kwargs):
    #     #NOTE: To inherit the private attribute '_id'
    #     if isinstance(value, BaseModel):
    #         # value_dict = dict(value)
    #         value_dict = value.model_dump()
    #         if '_id' in value.__private_attributes__:
    #             value_dict['id'] = str(value._id) # type: ignore
    #         elif 'id' in value_dict:
    #             value_dict['id'] = str(value_dict['id'])
    #     else:
    #         value_dict = value
    #         if '_id' in value_dict:
    #             value_dict['id'] = str(value['_id'])
    #         elif 'id' in value_dict:
    #             value_dict['id'] = str(value['id'])
    #     return super().model_validate(value_dict, *arg, **kwargs)



class Link(ClientModel):
    collection: str
    id: str


