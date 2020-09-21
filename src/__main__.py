import eel

eel.init('public')

@eel.expose
def handler(code: str):
    print(code)

eel.start('index.html')
