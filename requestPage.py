import wikipedia
import wolframalpha
from database import insertOneItem

while True:
    wikipedia.set_lang('hu')
    input = input("Write your searching message: ")

    try:
        app_id = ''
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
        

    except:
        result = wikipedia.summary(input,sentences=3)

        print(result)

        request = input
        if len(result) > 200:
            response = result[0:200]
        else:
            response = result

        insertOneItem(request, response)