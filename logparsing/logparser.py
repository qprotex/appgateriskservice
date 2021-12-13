import re


class LogParser:
    def __init__(self, func):
        self.execute = func
        #self.message = message
        #pass


    def execute(self):
        print("Original execution")


def ssh_parser(message):
    # declaring the regex pattern for IP addresses
    match = re.search(r'(\S+) password for.*?(\S+) from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', message)
    if match:
        return {
            "loginStatus": 1 if match.group(1) == "Accepted" else 0,
            "username": match.group(2).lower(),
            "ip": match.group(3)
        }
    else:
        return None


def other_parser():
    pass

#
# if __name__ == "__main__":
#     strat0 = LogParser()
#     strat1 = LogParser(ssh_parser)
#
#     strat0.execute()
#     strat1.execute()
