BASE_URL = "https://experimental.starforge.app/"
TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJmbGV4by1tbXMtYXVkaWVuY2UiLCJpc3MiOiJodHRwOi8vZmxleG8tbW1zLXNlcnZpY2VzIiwidXNlcm5hbWUiOiJ1c2VyMDEiLCJncm91cHMiOlsic3VwZXJfYWRtaW5zIl0sImV4cCI6MTgwMTIwOTYwMH0.xv6cRFq8KgtkuBJYGdwJSvgpktJUcWvsivSn9UJmwAk"

from mbse4u_sysmlv2_auth import configure_session, SysMLV2AuthError
configure_session(TOKEN, BASE_URL)  # once at startup
import mbse4u_sysmlv2_helpers as h
projects = h.get_projects(BASE_URL)
print(projects)
