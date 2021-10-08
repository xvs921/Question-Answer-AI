import wikipedia
import wolframalpha
from database import insertOneItem, findAllWhich

def requestHandle(input):
    wikipedia.set_lang('hu')
    #input = input("Write your searching message: ")

    try:
        app_id = 'EUT3JX-RUYX537GRV'
        client = wolframalpha.Client(app_id)
        request = client.query(input)
        result = next(request.results).text
        
        print(result)

        request = input
        if len(result) > 200:
            response = result[0:200]
        else:
            response = result

        insertOneItem(request, response)
        return response

    except:
        try:
            result = wikipedia.summary(input,sentences=3)

            print(result)

            request = input
            if len(result) > 200:
                response = result[0:200]
            else:
                response = result

            insertOneItem(request, response)
            return response
        except:
            print("There is an error!")
            return "Error"

def requestDatabase(operation, input):
    if operation == 'find':
        result = findAllWhich(input)
        return result

