from rolepermissions.roles import AbstractUserRole

class PageAdmin(AbstractUserRole):
	available_permissions = {
		'access_admin_dashboard':True,
		'edit_cover_image':True,
		'edit_background_image':True,
		'add_users':True,
		'delete_users':True,
	}

