from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
import gmplot
import codecs

#decode_hex('3B')[0]

app = Flask(__name__)


decode_hex = codecs.getdecoder("hex_codec")  #  hex decoder object 
commands = []   # store all the POST request commands here 


@app.route("/", methods = ['GET', 'POST'])
def base():
    return render_template('home.html')

@app.route("/home", methods = ['GET', 'POST'])
def home():

    counter = 0 

    #Hello;1234;testing@!#
    if request.method == 'POST':
        data = request.get_data()


        if data is not None:
            datastr = ''.join([chr(b) for b in data])
            split = datastr.split('&')
            print(split)
            
            message = split[2][8:].split('%')
            print(message)
            
            decoded_msg = ''

            for word in message:
                if len(word) > 2:
                    try:
                        #word[:2].decode('hex')
                        decode_hex(word[:2])[0]
                        print(decode_hex(word[:2])[0].decode('utf-8'))

                    except:
                        print('Could not be converted to hex')
                        decoded_msg += word
                    else:
                        #decoded_msg += word[:2].decode('hex') + word[2:]
                        decoded_msg += decode_hex(word[:2])[0].decode('utf-8') + word[2:]
                        

                elif len(word) == 2:
                    try: 
                        #word[:2].decode('hex')
                        decode_hex(word[:2])[0]
                    except:
                        print('Could not be converted to hex')
                        decoded_msg += word[:2]
                    else:
                        #decoded_msg += word[:2].decode('hex')
                        decoded_msg += decode_hex(word[:2])[0].decode('utf-8') + word[2:]


                else:
                    decoded_msg += word

            print(decoded_msg)
            counter += 1
            commands.append({'message': decoded_msg, 'count': counter})
            print(commands)

            if len(commands) > 10:
                del commands[: len(commands) - 1]
                counter = 0 
            
            return 'Request recieved'

    else:
        return 'Waiting for POST request'


@app.route("/csv", methods = ['GET', 'POST'])
def csv():
   
    if request.method == 'POST':
        file = request.files['csvfile']

        if not os.path.isdir('static'):
            os.mkdir('static')      
        
        filepath = os.path.join('static', file.filename)
        file.save(filepath)

        api_key = 'AIzaSyBE26vTcC2zmNuB_Q1X6i8UzKY-ca5Dfxc'

        df = pd.read_csv('static/{}'.format(file.filename))
        lat = df['latitude'].tolist()
        lng = df['longitude'].tolist()

        for i in range(len(lng)):
            lng[i] = ((abs(lng[i])- abs(lng[i])%100)/100 + abs(lng[i])%100/60)*-1
            print(lng[i])
            #lng[i] = (abs(int(str(lng[i]).split('.')[0][:2])) + float(str(lng[i]).split('.')[0][-2:]  + '.' + str(lng[i]).split('.')[-1])/60)*-1

        for i in range(len(lat)):
            lat[i] = (lat[i] - lat[i]%100)/100  + (lat[i]%100)/60
            print(lat[i], lat[i]%100)
            #lat[i] = int(str(lat[i]).split('.')[0][:s2]) + float(str(lat[i]).split('.')[0][-2:]  + '.' + str(lat[i]).split('.')[-1])/60
        
        gmap = gmplot.GoogleMapPlotter(lat[0], lng[0], 10, apikey = api_key)
        gmap.marker(lat[0], lng[0], label='Start')
        gmap.marker(lat[-1], lng[-1], label = 'End')
        gmap.scatter(lat, lng, 'red', size = 750, marker = False)
        gmap.plot(lat, lng, 'blue', edge_width=3) # joins plot
        gmap.draw('templates/{}map.html'.format(file.filename)) 

        return render_template('{}map.html'.format(file.filename))
    
    return render_template('csv.html')

@app.route('/message', methods = ['GET', 'POST'])
def message():
    return render_template('message.html', command = commands)


if __name__ == '__main__':
    app.run(debug=True)

    ## home should have three buttons : message, csv (To see path), and send command 
    ## make a table of all messages (create a static directory for messages )





"""
def home():

    #Hello;1234;testing@!#
    if request.method == 'POST':
        data = request.get_data()

        if data is not None:
            datastr = ''.join([chr(b) for b in data])
            split = datastr.split('&')
            print(split)
            
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

            return render_template('message.html', decoded_msg = decoded_msg)

    return 'Waiting for POST request'

"""