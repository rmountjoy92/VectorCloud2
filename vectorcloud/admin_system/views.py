from flask_admin.contrib.fileadmin import FileAdmin
from flask_login import current_user
from flask import redirect, url_for
from vectorcloud.paths import plugins_folder
from vectorcloud import admin


class PluginsView(FileAdmin):
    def is_accessible(self):
        return current_user.role in ["superadmin", "admin"]

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("permission_denied.index"))


admin.add_view(PluginsView(plugins_folder, "/plugins/", name="Plugins"))
