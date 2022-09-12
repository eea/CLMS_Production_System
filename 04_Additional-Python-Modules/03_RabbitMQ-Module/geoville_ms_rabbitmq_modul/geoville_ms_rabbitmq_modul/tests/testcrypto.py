x = "gAAAAABdi5S2tSlgbOlAlgUR9J9JUtFgumru-IjN5YB2Mfhc6J1LOJnrVXSucoi71cv9Jhz4BAsolzuS1FzxWLB00l9-goUYwURkunU_mQXJdRxDE2-WHJ8988LjZ4l5fpy9o50kJU_2AeqxxPx6qVpExOlVFvVcCKVJnLaz4CO0XFAJyjMBsljzl69xh1cNguBbSGchhumqIiIurxcE0evAE3_ama7jjg1vRB8RBL1Zpg0Jr4iLzyNE5cFT45yggbDv7JOXrNBDKSTGFBBWsqSqWpLOniw47w_PT--9b1Q6_ANNjlJBI3i9Qpixo7SUVCl4Fzw6EU8obhgPnrl5e2yuOFxzJaHYUg=="
from cryptography.fernet import Fernet
x = bytes(x, 'utf-8')
cipher_suite = Fernet("Plcl5q-wJP1CfvKMk_h0kiuo0Hexf-BIgXB74L7gVlI=")

plain_text = cipher_suite.decrypt(x)
print(" [x] decrytped %r" % str(plain_text, 'utf-8'))

#geoville_message = json.loads(plain_text)