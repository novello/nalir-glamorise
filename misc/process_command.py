

class CommandProcessor:
    EXIT_COMMAND = "#exit"
    QUERY_COMMAND = "#query"


    def __init__(self):
        self.commands = [CommandProcessor.EXIT_COMMAND,\
        CommandProcessor.QUERY_COMMAND]

    def process_input(self, line):
        command = line.split(' ')[0]
        query = None
        if command in self.commands:
            if command == CommandProcessor.QUERY_COMMAND: 
                query = ' '.join(line.split(' ')[1:])
            else:
                query = command

        return query