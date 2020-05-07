import click
from virl.api import VIRLServer
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import warnings
from virl.helpers import get_cml_client
from .console.commands import console, console1
from .nodes.commands import nodes, nodes1
from .logs.commands import logs1
from .up.commands import up, up1
from .use.commands import use, use1
from .down.commands import down, down1
from .ls.commands import ls, ls1
from .save.commands import save, save1
from .telnet.commands import telnet, telnet1
from .ssh.commands import ssh, ssh1
from .generate import generate, generate1
from .start.commands import start, start1
from .stop.commands import stop, stop1
from .pull.commands import pull, pull1
from .search.commands import search, search1
from .swagger.commands import swagger, swagger1
from .uwm.commands import uwm1
from .viz.commands import viz, viz1
from .id.commands import id, id1
from .version.commands import version, version1
from .flavors import flavors1
from .images import images
from .cockpit.commands import cockpit


class CatchAllExceptions(click.Group):
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except Exception as exc:
            click.secho("Exception raised while running your command", fg="red")
            click.secho("Please open an issue and provide this info:", fg="red")
            click.secho("%s" % exc, fg="red")


@click.group(cls=CatchAllExceptions)
def virl():
    pass


def __get_server_ver():
    """
    Taste a VIRL/CML server and try and determine its version.

    Returns:
        string: Either '1' for VIRL/CML 1.x or the empty string for CML 2+
    """
    res = ""
    try:
        server = VIRLServer()
        # We don't care about cert validation here.  If this is a CML server,
        # we'll fail validation later anyway.
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        r = requests.get("https://{}/".format(server.host), verify=False)
        warnings.simplefilter("default", InsecureRequestWarning)
        r.raise_for_status()
        client = get_cml_client(server)
    except requests.HTTPError as he:
        if he.response.status_code == 403:
            # The user provided bad credentials, but the URL was valid, return empty
            pass
        else:
            res = "1"
    except:
        res = "1"

    return res


__server_ver = __get_server_ver()

if __server_ver == "1":
    virl.add_command(uwm1, name="uwm")
    virl.add_command(flavors1, name="flavors")
    virl.add_command(logs1, name="logs")
    virl.add_command(swagger1, name="swagger")
    virl.add_command(viz1, name="viz")
else:
    virl.add_command(cockpit)
    virl.add_command(images)

__sub_commands = [
    "console",
    "nodes",
    "up",
    "down",
    "ls",
    "use",
    "save",
    "telnet",
    "ssh",
    "generate",
    "start",
    "stop",
    "search",
    "pull",
    "id",
    "version",
]

for cmd in __sub_commands:
    virl.add_command(globals()[cmd + __server_ver], name=cmd)


if __name__ == "__main__":
    virl()  # pragma: no cover
