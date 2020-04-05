import configparser
import json
import os
from pathlib import Path
import re
import socket

from cryptography import x509
from cryptography.hazmat.backends import default_backend
import grpc
import requests
import anki_vector
from anki_vector import messaging


class ApiHandler:
    def __init__(self, headers: dict, url: str):
        self._headers = headers
        self._url = url

    @property
    def headers(self):
        return self._headers

    @property
    def url(self):
        return self._url


class Api:
    def __init__(self):
        self._handler = ApiHandler(
            headers={
                "User-Agent": f"Vector-sdk/{anki_vector.__version__}",
                "Anki-App-Key": "aung2ieCho3aiph7Een3Ei",
            },
            url="https://accounts.api.anki.com/1/sessions",
        )

    @property
    def name(self):
        return "Anki Cloud"

    @property
    def handler(self):
        return self._handler


def get_cert(serial):
    output = ""
    output += f"Using robot serial number: {serial} \n"
    output += "\nDownloading Vector certificate from Anki... \n"
    r = requests.get(
        "https://session-certs.token.global.anki-services.com/vic/{}".format(serial)
    )
    if r.status_code != 200:
        output += r.content
    cert = r.content
    return cert, serial, output


def user_authentication(session_id: bytes, cert: bytes, ip: str, name: str) -> str:
    # Pin the robot certificate for opening the channel
    output = ""
    creds = grpc.ssl_channel_credentials(root_certificates=cert)

    output += f"Attempting to download guid from {name} at {ip}:443... \n"

    channel = grpc.secure_channel(
        "{}:443".format(ip), creds, options=(("grpc.ssl_target_name_override", name,),)
    )

    # Verify the connection to Vector is able to be established (client-side)
    try:
        # Explicitly grab _channel._channel to test the underlying grpc channel directly
        grpc.channel_ready_future(channel).result(timeout=15)
    except grpc.FutureTimeoutError:
        output += f"\nUnable to connect to Vector\n Please be sure to connect via the Vector companion app first, and connect your computer to the same network as your Vector."

    try:
        interface = messaging.client.ExternalInterfaceStub(channel)
        request = messaging.protocol.UserAuthenticationRequest(
            user_session_id=session_id.encode("utf-8"),
            client_name=socket.gethostname().encode("utf-8"),
        )
        response = interface.UserAuthentication(request)
        if (
            response.code != messaging.protocol.UserAuthenticationResponse.AUTHORIZED
        ):  # pylint: disable=no-member
            output += f"\nFailed to authorize request:\n Please be sure to first set up Vector using the companion app."
    except grpc.RpcError as e:
        output += f"\nFailed to authorize request:\n An unknown error occurred '{e}'"

    output += "Done. \n"
    return response.client_token_guid, output


def get_session_token(api, username=None, password=None):
    output = ""
    payload = {"username": username, "password": password}
    r = requests.post(api.handler.url, data=payload, headers=api.handler.headers)
    if r.status_code != 200:
        output += r.content
    return json.loads(r.content), output


def standardize_name(robot_name):
    output = ""
    error = False
    # Extend the name if not enough is provided
    if len(robot_name) == 4:
        robot_name = "Vector-{}".format(robot_name.upper())
    # Fix possible capitalization and space/dash/etc.
    if re.match("[Vv]ector.[A-Za-z0-9]{4}", robot_name):
        robot_name = "V{}-{}".format(robot_name[1:-5], robot_name[-4:].upper())
    # Check that the end is valid
    if re.match("Vector-[A-Z0-9]{4}", robot_name):
        return robot_name, output
    output += (
        "Invalid robot name. Please match the format exactly. Example: Vector-A1B2 \n"
    )
    return robot_name, output


def get_name_and_ip(robot_name, ip):
    output = ""
    robot_name, out = standardize_name(robot_name)
    output += out
    output += f"Using robot name: {robot_name}\n"
    output += f"Using IP: {ip}\n"
    return robot_name, ip, output


def save_cert(cert, name, serial, anki_dir):
    """Write Vector's certificate to a file located in the user's home directory"""
    output = ""
    os.makedirs(str(anki_dir), exist_ok=True)
    cert_file = str(anki_dir / "{name}-{serial}.cert".format(name=name, serial=serial))
    output += f"Writing certificate file to '{cert_file}'...\n"
    with os.fdopen(os.open(cert_file, os.O_WRONLY | os.O_CREAT, 0o600), "wb") as f:
        f.write(cert)
    return cert_file, output


def validate_cert_name(cert_file, robot_name):
    """Validate the name on Vector's certificate against the user-provided name"""
    output = ""
    with open(cert_file, "rb") as f:
        cert_file = f.read()
        cert = x509.load_pem_x509_certificate(cert_file, default_backend())
        for fields in cert.subject:
            current = str(fields.oid)
            if "commonName" in current:
                common_name = fields.value
                if common_name != robot_name:
                    output += f"The name of the certificate ({common_name}) does not match the name provided ({robot_name}). Please verify the name, and try again. \n"
    return output


def write_config(serial, cert_file=None, ip=None, name=None, guid=None, clear=True):
    home = Path.home()
    config_file = str(home / ".anki_vector" / "sdk_config.ini")
    output = f"Writing config file to '{config_file}'..."

    config = configparser.ConfigParser(strict=False)

    try:
        config.read(config_file)
    except configparser.ParsingError:
        if os.path.exists(config_file):
            os.rename(config_file, config_file + "-error")
    if clear:
        config[serial] = {}
    if cert_file:
        config[serial]["cert"] = cert_file
    if ip:
        config[serial]["ip"] = ip
    if name:
        config[serial]["name"] = name
    if guid:
        config[serial]["guid"] = guid.decode("utf-8")
    temp_file = config_file + "-temp"
    if os.path.exists(config_file):
        os.rename(config_file, temp_file)
    try:
        with os.fdopen(os.open(config_file, os.O_WRONLY | os.O_CREAT, 0o600), "w") as f:
            config.write(f)
    except Exception as e:
        if os.path.exists(temp_file):
            os.rename(temp_file, config_file)
        raise e
    else:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    return output


def main(anki_email, anki_password, name, ip, serial):
    api = Api()
    output_all = ""
    error = False

    name, ip, output = get_name_and_ip(name, ip)
    output_all += output

    cert, serial, output = get_cert(serial)
    output_all += output

    home = Path.home()
    anki_dir = home / ".anki_vector"

    cert_file, output = save_cert(cert, name, serial, anki_dir)
    output_all += output

    output = validate_cert_name(cert_file, name)
    output_all += output

    token, output = get_session_token(api, anki_email, anki_password)
    if not token.get("session"):
        output += f"Session error: {token} \n"
    output_all += output

    guid, output = user_authentication(
        token["session"]["session_token"], cert, ip, name
    )
    output_all += output

    # Store credentials in the .anki_vector directory's sdk_config.ini file
    output = write_config(serial, cert_file, ip, name, guid)
    output_all += output
    return output_all, error
