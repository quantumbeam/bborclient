from os import linesep as br
from typing import TYPE_CHECKING, Any, Annotated
from typing_extensions import TypeAlias
from pydantic import BaseModel, ConfigDict, PlainSerializer



indent_unit = ' '*2
def repr_value(value, depth) -> str:
    ind1 = indent_unit * depth
    ind2 = indent_unit * (depth + 1)
    if isinstance(value, list):
        if len(value)==0:
            return '[]'
        prefix = f'['
        sep = f',{br}{ind2}'
        elements = f'{br}{ind2}' + sep.join(repr_value(e, depth+1) for e in value)
        suffix = f'{br}{ind1}]'
        return prefix + elements + suffix
    elif isinstance(value, BaseModel):
        prefix = f'{value.__repr_name__()}('
        sep = f',{br}{ind2}'
        elements = f'{br}{ind2}' + sep.join(f'{k}={repr_value(v, depth+1)}' for k,v in value.__repr_args__())
        suffix = f'{br}{ind1})'
        return prefix + elements + suffix
    else:
        return repr(value)


class ClientModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        populate_by_name = True,
        str_max_length=1000,
        use_attribute_docstrings = True,
    )

    def __repr__(self, depth=0):
        return repr_value(self, depth)
    
    def keys(self):
        return self.__dict__.keys()

    def keylist(self):
        return list(self.keys())
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





# Define ObjectId and DBRef depending on the availability of bunnet


class DBRef_(ClientModel):
    collection: str
    id: str

if TYPE_CHECKING:
    from bunnet import PydanticObjectId
    from bson import DBRef
    ObjectId: TypeAlias = 'PydanticObjectId | str'
    Link: TypeAlias = 'DBRef | DBRef_'
else:
    try:
        from bunnet import PydanticObjectId
        from bson import DBRef
        HAS_BUNNET = True

        def serialize_dbref(obj: DBRef|dict|list) -> str|Any:
            if isinstance(obj, DBRef):
                return {"collection": obj.collection, "id": str(obj.id)}
            elif isinstance(obj, dict):
                return {k: serialize_dbref(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple, set)):
                t = type(obj)
                return t(serialize_dbref(v) for v in obj)
            else:
                return str(obj)
    except ImportError:
        HAS_BUNNET = False

    ObjectId = PydanticObjectId if HAS_BUNNET else str
    Link = Annotated[DBRef, PlainSerializer(serialize_dbref)] if HAS_BUNNET else DBRef_


    