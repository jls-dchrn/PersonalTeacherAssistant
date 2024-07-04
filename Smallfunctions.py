from openai import OpenAI
import os
import csv


class gpt():

    def __init__(self):

        self.model = "gpt-4o"
        self.client = OpenAI(api_key=os.environ.get("MI_CHATGPT_APIKEY"))
        # Use "Export MI_CHATGPT_APIKEY=xxxxxxxxxxxxxxx" to get api access

        self.sessionmemory = ""
    """ 
    model

    SessionMemory

    initial prompt

    summarization prompt

    context file

    """

    # Ask user for username, and return context file. Add new contextfile if username wasnt found
    # Hayato
    # Takumi
    def login():
        print("This is test")
        pass
    

    # create context file for new user with an existing template
    # the template could contain, name, level, previous summarizations

    # Hayato
    # Takumi
    def createFile():
        pass

    # basic call to gpt api
    #Nikolaj
    # Input Messages as List<String>
    def sendMessage(self, messages):
        completion = self.client.chat.completions.create(
            model = self.model,
            messages = messages)
        return completion

    
    # use sendMessage to summarize session with summarize prompt, and save it into the context file
    #Nikolaj
    #Input name of User as string
    def _summarize(self, user):
        # Context of user that will be updated:
        usercontext = []

        #First find the user's context file or create a new
        contextfile = "/contextfiles/CF" + user + ".csv" 
        if os.path.exists(contextfile):
            with open(contextfile ,"r") as f:
                usercontext = list(csv.reader(f))
        else:
            with open(contextfile,"w") as f:
                pass
        
        # Prompt for summary after a teaching session
        summaryprompt = f"You are a personal teaching assistant, and you have just finished tutoring a session.
            You now want to adapt your future teaching methods to adopt to this specific student.
            This is the current session memory: {self.sessionmemory}.
            Expand your knowledge of the student and what teaching methods they repond to, to the following csv file: {usercontext}"


        #get the resonse from the model
        response = self._sendMessage({"role":"system", "content": summaryprompt})
        summary = response.choices[0].message["content"]

        #Update the user context and write to the context file:
        usercontext.append([summary])
        with open(contextfile, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerows(usercontext)






    # use sendMessage and SessionMemory for the user to ask questions
    """ 
    Login
    Loop:
        User asks question
        Model responds
        Model asks if user wants to continue / (rating system for model)
    Summarize session
    """
    # Jules
    def discuss():
        pass

    # resize image and file format to standard format
    #Jules
    def imagePrep():
        pass











