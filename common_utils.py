

class Question:

    def __init__(self, id : int = -1,question : str = None, options : list = None, string :str= None):
        if string:
            self.id, self.question, opt_string = string.split('|')
            self.options = list(opt_string.split('-'))
            self.id = int(self.id)
        elif (question == None or options == None or id==-1):
            raise Exception("Enter either serialised string or the tha parameters.")
        else:
            self.id = id
            self.question = question
            self.options = options

    def ask(self):
        print(f'[Q] {self.question}')
        for opt in self.options:
            print('\t',opt)
        answered = input('#> ').strip().lower()
        if len(answered) > 1:
            print('Please input the option label (a/b/c/d/...)')
            return self.ask()
        return ord(answered)-ord('a')
    
    def serialize(self):
        out = str(self.id)+'|'+ self.question + '|' + '-'.join(self.options)
        return out
