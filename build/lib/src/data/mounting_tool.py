import os
import sys


class MountData:
    def __init__(self, user: str,
                 password: str = None):
        self.user = user
        self.password = password

    def create_mount(self, mount_source: str, mount_target: str):
        """This function creates a mount between a source and a target.


        Args:
            mount_source (str, optional): Machine where data is stored.
            mount_target (str, optional): _description_. Defaults to None.
        """
        os.system(self._mount_command(self.user,
                                    self.password,
                                    mount_source,
                                    mount_target))
        

    def _mount_command(self, user,
                      password,
                      mount_source="brildev1:/brildata/22/",
                      mount_target="./Files/22"):
        """This function creates a mount string to be excecuted
           as a system command."""
        # if mount source is not a directory, create it
        if not os.path.isdir(mount_target):
            print("Mount target is not a directory. Creating it...")
            os.makedirs(mount_target)
        return f"""sshfs -o reconnect -o password_stdin \
                -oProxyCommand="ssh -W %h:%p {user}@cmsusr.cern.ch" \
                {mount_source} {mount_target} <<< '{password}'"""


