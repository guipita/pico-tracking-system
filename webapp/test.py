import codecs

a = '3B'
print(a.decode('hex'))
decode_hex = codecs.getdecoder("hex_codec")
print(decode_hex('3B')[0])
print(type(decode_hex('3B')[0]))

test = 'Status=received&ApiVersion=v1&Command=Hello%3B1234%3Btesting%40%21%23&SimUniqueName=project&Payload=Hello%3B1234%3Btesting%40%21%23&SimSid=HS670d39f0347a1693070ec788bb2164ad&Direction=from_sim&CommandSid=HC3a954faf5a5573c0240be1e2701fef9e&AccountSid=AC24e93e3663f305d82c15493ff7bd2558&PayloadType=text'
split = test.split('&')
print(split)


# Hello;1234;testing@!#

message = split[2][8:].split('%')
print(message)
decoded_msg = ''


for word in message:
    if len(word) > 2:
        try:
            word[:2].decode('hex')
        except:
            print('Could not be converted to hex')
            decoded_msg += word
        else:
            decoded_msg += word[:2].decode('hex') + word[2:]
            

    elif len(word) == 2:
        try: 
            word[:2].decode('hex')
        except:
            print('Could not be converted to hex')
            decoded_msg += word[:2]
        else:
            decoded_msg += word[:2].decode('hex')

    else:
        decoded_msg += word

print(decoded_msg)


