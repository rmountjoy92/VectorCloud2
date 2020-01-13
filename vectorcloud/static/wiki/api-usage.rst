REST API Usage
==============

All REST API endpoints accept POST requests. All resources require the following:
 - API key
 - Arguments for the function that the endpoint calls

Example:
    To make Vector say 'ping' using the rest api, we would use the RobotDo resource and
    provide: api_key, vector_id, and commands

      .. code-block:: python

        from requests import put
        put('http://localhost:4999/api/robot_do', data={'api_key': '123456789', 'vector_id': 1, 'commands': 'robot.behavior.say_text("ping")'}).json()
