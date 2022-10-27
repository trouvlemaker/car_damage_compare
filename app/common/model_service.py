import traceback
import numpy as np
import json
from decimal import Decimal
json.encoder.FLOAT_REPR = lambda f: ("%.4f" % f)
try:
    import tritonclient.grpc as grpcclient
    import tritonclient.http as httpclient
    from tritonclient.utils import InferenceServerException
except Exception as e:
    print('Triton Client not imported.')


STRING_TO_NUMPY = {
    'BOOL': np.bool,
    'UINT8': np.uint8,
    'UINT16': np.uint16,
    'UINT32': np.uint32,
    'UINT64': np.uint64,
    'INT8': np.int8,
    'INT16': np.int16,
    'INT32': np.int32,
    'INT64': np.int64,
    'FP16': np.float16,
    'FP32': np.float32,
    'FP64': np.float64,
    'STRING': np.bytes_
}


def string_to_numpy(type_string):
    return STRING_TO_NUMPY[type_string]


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        else:
            return json.JSONEncoder.default(self, obj)


class SodaModelService:

    def __init__(self, server_url, model_name, model_version=None):
        self.server_url = server_url
        self.model_name = model_name
        self.model_version = model_version if model_version else ""
        self.inputs = list()
        self.outputs = list()

    def add_inputs(self, inputs: list):
        for input in inputs:
            t_shape = input['shape']
            dtype = input['dtype']
            np_data = input["input_tensor"].astype(string_to_numpy(dtype))
            self.add_input(
                name=input['name'],
                shape=t_shape,
                dtype=dtype,
                tensor=np_data
            )

    def add_outputs(self, outputs: list):
        for output in outputs:
            self.add_output(output['name'])

    def add_input(self, name, shape, dtype, tensor):
        triton_input = grpcclient.InferInput(name, shape, dtype)
        triton_input.set_data_from_numpy(tensor)
        self.inputs.append(triton_input)

    def add_output(self, name):
        self.outputs.append(grpcclient.InferRequestedOutput(name))

    def get_model_config(self):
        try:
            server_url = f'{self.server_url}:8001'
            triton_client = grpcclient.InferenceServerClient(
                url=server_url,
                verbose=False
            )
        except Exception as e:
            print("context creation failed: " + str(e))
            raise e

        # Metadata
        metadata = triton_client.get_model_config(
            self.model_name,
            as_json=True
        )
        # if not (metadata['name'] == self.model_name):
        #     raise Exception("FAILED : get_model_metadata")

        return metadata

    def get_model_meta_data(self):
        try:
            server_url = f'{self.server_url}:8001'
            triton_client = grpcclient.InferenceServerClient(
                url=server_url,
                verbose=False
            )
        except Exception as e:
            print("context creation failed: " + str(e))
            raise e

        # Metadata
        metadata = triton_client.get_model_metadata(
            model_name=self.model_name,
            model_version=self.model_version,
            as_json=True
        )
        if not (metadata['name'] == self.model_name):
            raise Exception("FAILED : get_model_metadata")

        return metadata

    def predict(self):
        try:
            server_url = f'{self.server_url}:8001'
            triton_client = grpcclient.InferenceServerClient(
                url=server_url,
                verbose=False
            )
        except Exception as e:
            print("channel creation failed: " + str(e))
            raise e

        try:
            # Test with outputs
            results = triton_client.infer(
                model_name=self.model_name,
                model_version=self.model_version,
                inputs=self.inputs,
                outputs=self.outputs,
                client_timeout=None
            )
        except Exception as e:
            print(traceback.format_exc())
            raise e
        else:
            
            results.get_response()

            # outputs = [{output.name(): results.as_numpy(output.name())} for output in self.outputs]

            out_dict = {}

            # each output loop
            for output in self.outputs:

                result = results.as_numpy(output.name())
                
                # batch loop
                for re in result:

                    new_output = []

                    for box, polygons, label, score in re:

                        new_box = np.array(box.decode().strip('[]').split(',')).astype(np.int32).tolist()
                        new_polygon = np.array(polygons.decode().strip('[]').split(',')).astype(np.int32).reshape(4,2).tolist()
                        new_label = int(label.decode())
                        new_score = float(score.decode())

                        new_output.append([new_box,new_polygon,new_label,new_score])

                    out_dict[output.name()] = new_output
            
            return out_dict