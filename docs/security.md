# Security

Passwords are bcrypt hashed; JWTs are validated; RBAC protects curator/admin endpoints; uploads validate type, size, dimensions, and content; filenames are generated; CORS and security headers are configured; errors avoid secret disclosure; audit logs track privileged changes.
