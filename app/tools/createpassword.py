from passlib.handlers import argon2

test = argon2.argon2.encrypt("r3dbu11r4c1ng")
print(test)
print(argon2.argon2.verify("r3dbu11r4c1ng", test))