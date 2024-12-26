import datetime
import json
from typing import List, Dict

#Define a class to manage individual poll logic
class PollSystem:
    def __init__(self, question, options, start_date, end_date, answers=None):
        self.question = question
        self.options = options
        self.start_date = start_date
        self.end_date = end_date
        self.answers = answers or {option: 0 for option in options} #If 'answers' is None, each option is initialized to 0.

    #Check if the poll is currently active
    def poll_active(self):
        now = datetime.datetime.now()
        return self.start_date <= now <= self.end_date

    #Add a vote to the chosen option
    def vote(self, option):
        option = option.strip() #Clean up extra spaces
        if not self.poll_active():
            raise Exception("Poll is not active.")
        if option not in self.options:
            raise ValueError("Please choose a valid option.") #Invalid option chosen
        self.answers[option] += 1 #Increment vote count for the chosen option

    #Get the poll answers
    def generate_report(self):
        return self.answers

    #Convert poll data to a dictionary (to save to a file)
    def to_dict(self) -> Dict:
        return {
            "question": self.question,
            "options": self.options,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "answers": self.answers,
        }

    #Create a Poll System object from a dictionary (to load from a file)
    @staticmethod
    def from_dict(data):
        answers = data.get("answers", {option: 0 for option in data["options"]})
        return PollSystem(
            question=data["question"],
            options=data["options"],
            start_date=datetime.datetime.fromisoformat(data["start_date"]),
            end_date=datetime.datetime.fromisoformat(data["end_date"]),
            answers=answers,
        )
#Define a class to manage multiple polls and handle saving/loading
class PollManager:
    def __init__(self, save_file="polls.json"):
        self.polls = []
        self.save_file = save_file
        self.load_polls()

    #Create a new poll
    def new_poll(self, question, options, start_date, end_date):
        if start_date >= end_date:
            raise ValueError("Start date must be before end date.")
        poll = PollSystem(question, options, start_date, end_date)
        self.polls.append(poll)
        self.save_polls()
        return poll

    #Get all active polls
    def get_active_polls(self):
        return [poll for poll in self.polls if poll.poll_active()]

    #Analyze results of all polls
    def analyze_results(self):
        return [{"question": poll.question, "results": poll.generate_report()} for poll in self.polls]

    #Save all polls to a file
    def save_polls(self):
        with open(self.save_file, "w") as f:
            json.dump([poll.to_dict() for poll in self.polls], f)

    #Load polls from a file
    def load_polls(self):
        try:
            with open(self.save_file, "r") as f:
                polls_data = json.load(f)
                self.polls = [PollSystem.from_dict(data) for data in polls_data]
        except (FileNotFoundError, json.JSONDecodeError):
            self.polls = [] #If file doesn't exist or is invalid, start with an empty list

#Define a class to represent a user interacting with the poll system
class User:
    def __init__(self, user_id, poll_manager):
        self.user_id = user_id
        self.poll_manager = poll_manager

    #Let the user vote in an active poll
    def respond_to_poll(self):
        active_polls = self.poll_manager.get_active_polls() #Get active polls
        if not active_polls:
            print("No active polls available.")
            return

        print("Active polls:")
        for idx, poll in enumerate(active_polls, start=1):
            print(f"{idx}. {poll.question}")

        try:
            poll_choice = int(input("Choose a poll number to vote in: ")) - 1
            if poll_choice < 0 or poll_choice >= len(active_polls):
                print("Invalid choice.")
                return

            poll = active_polls[poll_choice]
            print(f"Options: {', '.join(poll.options)}")
            user_choice = input("Enter your choice: ")

            poll.vote(user_choice)
            self.poll_manager.save_polls()
            print(f"Thank you for voting! You chose: {user_choice}")
        except Exception as e:
            print(f"Error: {e}")

    #Let the user create a new poll
    def new_poll(self):
        try:
            question = input("Enter the poll question: ")
            options = input("Enter poll options (separated by commas): ").split(",")
            start_date_str = input("Enter the start date (YYYY-MM-DD): ")
            end_date_str = input("Enter the end date (YYYY-MM-DD): ")

            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

            poll = self.poll_manager.new_poll(question, [option.strip() for option in options], start_date, end_date)
            print(f"Poll created successfully: {poll.question}")
        except Exception as e:
            print(f"Error creating poll: {e}")

    #Display results of all polls
    def show_results(self):
        results = self.poll_manager.analyze_results()
        if not results:
            print("No polls available.")
            return

        for result in results:
            print(f"Question: {result['question']}")
            for option, count in result['results'].items():
                print(f"  {option}: {count} votes")
#Main Poll System logic
if __name__ == "__main__":
    poll_manager = PollManager() #Initialize the PollManager
    user = User("username", poll_manager) #Create a User instance

    while True:
        #Display main menu options
        print("\nMain Menu:")
        print("1. Create a new poll")
        print("2. Vote in an active poll")
        print("3. View poll results")
        print("4. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            user.new_poll() #User creates a new poll
        elif choice == "2":
            user.respond_to_poll() #User votes in a poll
        elif choice == "3":
            user.show_results() #Display poll results
        elif choice == "4":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.") #If the user enters an invalid choice, return to the main menu