import httpx
import json

class Service:
    def __init__(self, labels: dict[str, dict[str, list[str]]],
                 precisions: dict[str, dict[str, float | str]]):
        """
        Wrapper over each model, to handle exceptions and errors.
        The precisions can be a different thing for each model, so
        check the doc for the speficied model.
        """

        self.name = "GenericModel"

        self._labels = labels
        self._precisions = precisions

    def generic_prompt(self, func_prompt, prompt: str):
        """
        :param func_prompt: a method like `model_tfidf.prompt()`.
        :param: prompt: The input argument of *func_prompt*.

        It returns `func_prompt(prompt)` but wrapped to catch errors
            and exceptions.

        If there is an error, it returns something as
        { 'error': 'message': "message error" }.
        """
        try:
            return func_prompt(prompt)

        except httpx.HTTPStatusError as e:
            print(f'\nHTTPStatusError: {e}\nResponse: {e.response.text}\n')
            name_func: str = func_query.__name__
            name_mod: str= func_query.__module__
            error_payload = {
                'error': {
                    'type': 'HTTPStatusError',
                    'message': f"From {name_func}() in {name_mod}:\
                        {e.response.status_code} {e.response.reason_phrase}",
                    'status_code': e.response.status_code,
                    'details': str(e.response.text)[:200]
                }
            }
            return error_payload

        except Exception as e:
            print(f'\nRuntimeError or other unhandled exception: {e}\n')
            error_payload = {
                'error': {
                    'type': 'ServerError',
                    'message': f"An unexpected error occurred \
                                on the server: {str(e)}"
                }
            }
            return error_payload

