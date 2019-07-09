# selectors for all items we are interested in
# Logging in
css_username_field = "input#Username"
css_password_field = "input#Password"
css_login_button = "input[value='Inloggen']"

# Wait for page load
css_wait_full_page = "#ana_1"
click_and_wait = click_and_wait_ie

# Deal with menu items
css_menu_id = "#ak"
css_menu_items = css_menu_id + " " + "a.enabled"
active_font_classname = "Font28"
css_menu_active_font = "." + active_font_classname
css_menu_active_item = css_menu_id + " " + css_menu_active_font

# Next page button
css_next_page_button = "#as"
