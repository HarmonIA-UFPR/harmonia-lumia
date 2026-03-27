import edwh_uuid7
import uuid

u = edwh_uuid7.uuid7()
print(type(u) == uuid.UUID)
print(u.version)
