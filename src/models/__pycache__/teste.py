import bcrypt

senha_digitada = "dbz"  # A senha real usada no cadastro
hash_no_banco = "$2b$12$dcs3NxpRf5tS/XTK0PhfK.rYnwhZ8qtJdX/VfxvR3LC4xBkv0xaA."  # Copiado do banco

# Converter hash para bytes, se necessário
if isinstance(hash_no_banco, str):
    hash_no_banco = hash_no_banco.encode('utf-8')

# Testar a senha
if bcrypt.checkpw(senha_digitada.encode('utf-8'), hash_no_banco):
    print("✅ Senha correta! Login deve funcionar.")
else:
    print("❌ Senha incorreta! A senha não bate com o hash no banco.")
