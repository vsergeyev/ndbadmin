from webapp2_extras.routes import RedirectRoute as Route

import admin


urlpatterns = [
    # Admin panel
    Route('/', admin.AdminHandler, 'admin_panel', strict_slash=True),
    # Real life usage:
    #Route('/admin/', admin.AdminHandler, 'admin_panel', strict_slash=True),
    # and CRUD - create/update, list, delete items
    Route('/admin/<model>/<action>/', admin.CrudHandler, 'admin_crud',
          strict_slash=True),
]