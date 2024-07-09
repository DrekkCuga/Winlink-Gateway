import exchangelib, json, maidenhead, bom, traceback, requests
import time
class EmailServer():

    def __init__(self, configFileName):
        self.config = json.load(open(configFileName, "r"))
        credentials = exchangelib.OAuth2Credentials(
            client_id=self.config["creds"]["exchange"]["client_id"],
            client_secret=self.config["creds"]["exchange"]["client_secret"],
            tenant_id=self.config["creds"]["exchange"]["tenant_id"],
            identity=exchangelib.Identity(smtp_address=self.config["email_address"])
        )
        emailConfig = exchangelib.Configuration(
            credentials=credentials,
            server='outlook.office365.com'
        )
        self.account = exchangelib.Account(self.config["email_address"], config=emailConfig, access_type=exchangelib.IMPERSONATION)

    def __processEmail(self, email):
        #Processes email, make sure to handle any responses in here as email will be marked as 'read' afterwards
        args = email.subject.lower().split(" ")
        email_from = email.author.email_address
        body = email.text_body
        print(f"Processing email - {email.subject} from {email_from}")
        if len(args) < 1:
            return
        print(args)
        try:
            if args[0] == "weather":
                try:
                    if args[1] == "grid":
                        lat, long = maidenhead.to_location(args[2])
                        forecast = bom.getClosestForecast(lat,long)["forecast"]
                        data = bom.getForecast(forecast)
                        print(f"Sending Weather Report for { args[2] } to {email_from}")
                        self.sendEmail(email_from, "VK3MAG BOM Weather Report for " + args[2], data)

                    elif args[1] == "coord":
                        lat = float(args[2])
                        long = float(args[3])
                        forecast = bom.getClosestForecast(lat,long)["forecast"]
                        data = bom.getForecast(forecast)
                        grid = maidenhead.to_maiden(lat, long)
                        print(f"Sending Weather Report for { grid } to {email_from}")
                        self.sendEmail(email_from, "VK3MAG BOM Weather Report for " + grid, data)

                except IndexError:
                    self.sendEmail(email_from, "VK3MAG Winlink ERROR", f"Invalid usage, usage is:\n\"weather grid <grid>\" OR \"weather coord <lat> <long>\"")
                except TypeError:
                    self.sendEmail(email_from, "VK3MAG Winlink ERROR", f"Invalid coordinates, usage is:\n\"weather grid <grid>\" OR \"weather coord <lat> <long>\"")
                
            elif args[0] == "message":
                if email_from.lower() not in self.config["allowed_to_message"]:
                    print(f"Disallowed user {email_from} tried to send a message!")
                    self.sendEmail(email_from, "VK3MAG Winlink ERROR", f"User {email_from} not allowed to send messages")
                    return
                print("allowed")
                if args[1] == "telegram":
                    apiURL = f'https://api.telegram.org/bot{ self.config["creds"]["telegram"]["api_token"] }/sendMessage'
                    print(f"User {email_from} sent a telegram message!")
                    response = requests.post(apiURL, json={'chat_id': self.config["creds"]["telegram"]["chat_id"], 'text': f"User {email_from} send a message:\n{body}"})
                    if response.status_code != 200:
                        self.sendEmail(email_from, "VK3MAG Winlink ERROR", f"Failed to send telegram message, error code {response.status_code}")
                        print(f"Failed to send a telegram message, status code: {response.status_code}\n{response.json}")
                        return
                    self.sendEmail(email_from, "VK3MAG Winlink Message Sent", f"Telegram Message successfully sent. Message content is:\n\n" + body)
                elif args[1] == "discord":
                    if args[2] not in self.config["discord_channels"].keys():
                        channel_list = "\n".join(self.config["discord_channels"].keys())
                        self.sendEmail(email_from, "VK3MAG Winlink ERROR", f'Channel not valid, valid channels are: { channel_list }')
                        return
                    post_data = {"content": f"User {email_from} send a message:\n{body}"}
                    print(f"User {email_from} sent a discord message to channel {args[2]}!")
                    resp = requests.post(self.config["discord_channels"][args[2]], json=post_data)
                    if resp.status_code != 204:
                        print(f"Failed to send a discord message, error {resp.status_code}\n{resp.json}")
                        self.sendEmail(email_from, "VK3MAG Winlink ERROR", f"Failed to send discord message, error code { resp.status_code }")
                        return
                    self.sendEmail(email_from, "VK3MAG Winlink Message Sent", f"Discord Message successfully sent. Message content is:\n\n" + body)
            else:
                body = "Usage:\n"
                body += "\t'Weather Coord <lat> <long>' - Gets the closest BOM Forecast to specified coords (eg 'Weather Coord -37.82, 144.95') , only works in VK3 currently\n"
                body += "\t'Weather Grid <grid>' - Gets the closest BOM Forecast for the specified grid square (eg 'Weather Grid QF23'), only works in VK3 currently\n"

                if email_from.lower()  in self.config["allowed_to_message"]:
                    body += "\t'Message Telegram' - Sends a message to the linked Telegram channel, message content is the body of the email\n"
                    body += "\t'Message Discord <channel>' - Sends a message to the specified Discord channel.\n"
                    body += "\tAvailable Discord channels are:\n"

                    for channel in self.config["discord_channels"].keys():
                        body += f'\t\t{channel}\n'
                body += "\nDeveloped by VK3MAG"
                print(f"Processing help command for user {email_from}")
                self.sendEmail(email_from, "VK3MAG Winlink HELP", body)

        except Exception as e:
            #We errored, send the error back
            data = traceback.format_exc()
            self.sendEmail(email_from, "VK3MAG Winlink ERROR", data)

    def sendEmail(self, to, subject, body):
        msg = exchangelib.Message(
            account = self.account,
            subject=subject,
            body = body,
            to_recipients = [to]
        )
        msg.send()

    def check(self):
        for email in self.account.inbox.filter(is_read=False):
            self.__processEmail(email)
            email.is_read = True
            email.save()

if __name__ == "__main__":
    srv = EmailServer("config.json")
    while True:
        srv.check()
        print("Finished Checking")
        time.sleep(60)