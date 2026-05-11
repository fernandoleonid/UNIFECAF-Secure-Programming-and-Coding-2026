import hashlib
import bcrypt
import time
# ==============================================================================
# VULNERABILIDADE: MD5 E SHA para senha não usar
# ==============================================================================
plantext_password = 'fernandoleonid'
md5_password_1 = hashlib.md5(plantext_password.encode()).hexdigest()
md5_password_2 = hashlib.md5(plantext_password.encode()).hexdigest()
sha256_password = hashlib.sha256(plantext_password.encode()).hexdigest()

print ('='*40)
print ('❌ Senha insegura')
print (plantext_password)
print (md5_password_1)
print (md5_password_2)
print (sha256_password)

# ==============================================================================
# ✅ CORREÇÃO: bcrypt
# ==============================================================================
print ('='*40)
start_time = time.time()
bcrypt_password_1 = bcrypt.hashpw(plantext_password.encode(), bcrypt.gensalt())
elapsed_time_1 = time.time() - start_time

start_time = time.time()
bcrypt_password_2 = bcrypt.hashpw(plantext_password.encode(), bcrypt.gensalt(rounds=4))
elapsed_time_2 = time.time() - start_time

start_time = time.time()
bcrypt_password_3 = bcrypt.hashpw(plantext_password.encode(), bcrypt.gensalt(rounds=12))
elapsed_time_3 = time.time() - start_time

start_time = time.time()
bcrypt_password_4 = bcrypt.hashpw(plantext_password.encode(), bcrypt.gensalt(rounds=16))
elapsed_time_4 = time.time() - start_time



print ('='*40)
print ('✅ Senha segura')
print (bcrypt_password_1, elapsed_time_1)
print (bcrypt_password_2, elapsed_time_2)
print (bcrypt_password_3, elapsed_time_3)
print (bcrypt_password_4, elapsed_time_4)

